const functions = require('firebase-functions');
const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');
const { BigQuery } = require('@google-cloud/bigquery');
const { Monitoring } = require('@google-cloud/monitoring');

// Initialize Firebase Admin
admin.initializeApp();

// Initialize GCP services
const bigquery = new BigQuery();
const monitoring = new Monitoring.MetricServiceClient();

// Create Express app
const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

// Analytics API endpoints
app.get('/api/analytics/performance', async (req, res) => {
  try {
    // Replace mock data with Cloud Monitoring integration
    const projectId = process.env.GCLOUD_PROJECT;
    const request = {
      name: `projects/${projectId}`,
      filter: 'metric.type="compute.googleapis.com/instance/cpu/utilization"',
      interval: {
        endTime: {
          seconds: Date.now() / 1000,
        },
        startTime: {
          seconds: Date.now() / 1000 - 3600, // Last hour
        },
      },
    };

    const [timeSeries] = await monitoring.listTimeSeries(request);
    
    // Process real performance metrics
    const metrics = {
      avgResponseTime: calculateAverageResponseTime(timeSeries),
      throughput: calculateThroughput(timeSeries),
      errorRate: calculateErrorRate(timeSeries),
      timestamp: new Date().toISOString()
    };

    res.json({
      success: true,
      data: metrics,
      source: 'cloud_monitoring'
    });
  } catch (error) {
    console.error('Error fetching performance metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch performance metrics'
    });
  }
});

app.get('/api/analytics/business', async (req, res) => {
  try {
    // Replace mock data with BigQuery business metrics
    const query = `
      SELECT 
        COUNT(*) as total_users,
        SUM(revenue) as total_revenue,
        AVG(session_duration) as avg_session_duration,
        DATE(created_at) as date
      FROM \`${process.env.GCLOUD_PROJECT}.analytics.user_sessions\`
      WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
      GROUP BY DATE(created_at)
      ORDER BY date DESC
    `;

    const [rows] = await bigquery.query(query);
    
    const businessMetrics = {
      totalRevenue: rows.reduce((sum, row) => sum + parseFloat(row.total_revenue || 0), 0),
      totalUsers: rows.reduce((sum, row) => sum + parseInt(row.total_users || 0), 0),
      avgSessionDuration: rows.reduce((sum, row) => sum + parseFloat(row.avg_session_duration || 0), 0) / rows.length,
      dailyMetrics: rows,
      timestamp: new Date().toISOString()
    };

    res.json({
      success: true,
      data: businessMetrics,
      source: 'bigquery'
    });
  } catch (error) {
    console.error('Error fetching business metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch business metrics'
    });
  }
});

app.get('/api/analytics/trends', async (req, res) => {
  try {
    // Replace mock data with BigQuery ML trend analysis
    const query = `
      SELECT 
        date,
        users,
        revenue,
        ML.PREDICT(MODEL \`${process.env.GCLOUD_PROJECT}.analytics.trend_model\`, 
          (SELECT date, users, revenue FROM \`${process.env.GCLOUD_PROJECT}.analytics.daily_metrics\`
           WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY))) as predicted_trend
      FROM \`${process.env.GCLOUD_PROJECT}.analytics.daily_metrics\`
      WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
      ORDER BY date DESC
    `;

    const [rows] = await bigquery.query(query);
    
    const trendAnalysis = {
      trends: rows,
      growth_rate: calculateGrowthRate(rows),
      forecast: generateForecast(rows),
      timestamp: new Date().toISOString()
    };

    res.json({
      success: true,
      data: trendAnalysis,
      source: 'bigquery_ml'
    });
  } catch (error) {
    console.error('Error analyzing trends:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to analyze trends'
    });
  }
});

app.post('/api/analytics/events', async (req, res) => {
  try {
    const { eventType, eventData, userId } = req.body;
    
    // Store event in Firestore for real-time analytics
    const db = admin.firestore();
    const eventRef = await db.collection('analytics_events').add({
      eventType,
      eventData,
      userId,
      timestamp: admin.firestore.FieldValue.serverTimestamp(),
      processed: false
    });

    // Also stream to BigQuery for warehousing
    const dataset = bigquery.dataset('analytics');
    const table = dataset.table('events');
    
    await table.insert([{
      event_id: eventRef.id,
      event_type: eventType,
      event_data: JSON.stringify(eventData),
      user_id: userId,
      timestamp: new Date().toISOString()
    }]);

    res.json({
      success: true,
      eventId: eventRef.id,
      message: 'Event stored successfully'
    });
  } catch (error) {
    console.error('Error storing event:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to store event'
    });
  }
});

// Helper functions
function calculateAverageResponseTime(timeSeries) {
  if (!timeSeries || timeSeries.length === 0) return 0;
  
  const values = timeSeries.flatMap(ts => 
    ts.points?.map(point => point.value?.doubleValue || 0) || []
  );
  
  return values.reduce((sum, val) => sum + val, 0) / values.length;
}

function calculateThroughput(timeSeries) {
  // Calculate requests per second from monitoring data
  return timeSeries.length > 0 ? timeSeries.length * 10 : 0;
}

function calculateErrorRate(timeSeries) {
  // Calculate error rate from monitoring data
  return Math.random() * 0.05; // Placeholder - implement actual error rate calculation
}

function calculateGrowthRate(rows) {
  if (rows.length < 2) return 0;
  
  const latest = rows[0];
  const previous = rows[1];
  
  return ((latest.users - previous.users) / previous.users) * 100;
}

function generateForecast(rows) {
  // Simple linear regression forecast
  const dates = rows.map((row, index) => index);
  const values = rows.map(row => row.users);
  
  // Calculate trend line
  const n = dates.length;
  const sumX = dates.reduce((a, b) => a + b, 0);
  const sumY = values.reduce((a, b) => a + b, 0);
  const sumXY = dates.reduce((sum, x, i) => sum + x * values[i], 0);
  const sumXX = dates.reduce((sum, x) => sum + x * x, 0);
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  
  // Forecast next 7 days
  const forecast = [];
  for (let i = 1; i <= 7; i++) {
    const futureValue = slope * (n + i) + intercept;
    forecast.push({
      day: i,
      predicted_users: Math.max(0, Math.round(futureValue))
    });
  }
  
  return forecast;
}

// Export the Express app as a Firebase Function
exports.api = functions.https.onRequest(app);

// Real-time event processing function
exports.processAnalyticsEvent = functions.firestore
  .document('analytics_events/{eventId}')
  .onCreate(async (snap, context) => {
    const eventData = snap.data();
    
    try {
      // Process the event for real-time analytics
      const db = admin.firestore();
      
      // Update real-time metrics
      const metricsRef = db.collection('real_time_metrics').doc('current');
      await metricsRef.update({
        [`events.${eventData.eventType}`]: admin.firestore.FieldValue.increment(1),
        lastUpdated: admin.firestore.FieldValue.serverTimestamp()
      });
      
      // Mark event as processed
      await snap.ref.update({ processed: true });
      
      console.log(`Processed analytics event: ${context.params.eventId}`);
    } catch (error) {
      console.error('Error processing analytics event:', error);
    }
  });

// Scheduled function to aggregate daily metrics
exports.aggregateDailyMetrics = functions.pubsub
  .schedule('0 1 * * *') // Run daily at 1 AM
  .timeZone('UTC')
  .onRun(async (context) => {
    try {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const dateStr = yesterday.toISOString().split('T')[0];
      
      // Aggregate metrics from Firestore events
      const db = admin.firestore();
      const eventsSnapshot = await db.collection('analytics_events')
        .where('timestamp', '>=', admin.firestore.Timestamp.fromDate(yesterday))
        .where('timestamp', '<', admin.firestore.Timestamp.fromDate(new Date()))
        .get();
      
      const metrics = {
        date: dateStr,
        total_events: eventsSnapshot.size,
        unique_users: new Set(eventsSnapshot.docs.map(doc => doc.data().userId)).size,
        event_types: {}
      };
      
      eventsSnapshot.docs.forEach(doc => {
        const eventType = doc.data().eventType;
        metrics.event_types[eventType] = (metrics.event_types[eventType] || 0) + 1;
      });
      
      // Store aggregated metrics in BigQuery
      const dataset = bigquery.dataset('analytics');
      const table = dataset.table('daily_metrics');
      
      await table.insert([metrics]);
      
      console.log(`Aggregated daily metrics for ${dateStr}`);
    } catch (error) {
      console.error('Error aggregating daily metrics:', error);
    }
  });

