# Firebase Storage Integration for Aideon AI Lite

This document provides comprehensive information about the Firebase Storage integration for user-generated content management in Aideon AI Lite.

## Overview

Firebase Storage provides secure file uploads and downloads for your app. This integration enables Aideon AI Lite to handle user-generated content, project files, and media assets with enterprise-grade security and scalability.

## Features

- **Secure File Upload/Download**: Encrypted file storage with access control
- **Multiple File Types**: Support for images, documents, code files, audio, video, and archives
- **Intelligent File Organization**: Automatic path organization by user, project, and content type
- **File Validation**: Comprehensive validation for file types, sizes, and security
- **Signed URLs**: Secure, time-limited access to files
- **Storage Analytics**: Usage tracking and storage optimization
- **Direct Upload**: Client-side direct upload with signed URLs

## Architecture

### Components

1. **FirebaseStorageManager**: Core class for file operations
2. **Storage API Endpoints**: REST API for file management
3. **File Validation**: Security and type validation
4. **Path Management**: Organized storage structure
5. **Access Control**: Permission-based file access

### Storage Structure

```
aideonlite-ai.firebasestorage.app/
├── user-uploads/{user_id}/          # User-specific uploads
├── projects/{project_id}/           # Project-specific files
├── generated/{content_type}/        # AI-generated content
├── temp/                           # Temporary files
├── public/                         # Public assets
├── backups/{date}/                 # System backups
├── logs/{date}/                    # Application logs
└── exports/{user_id}/              # User data exports
```

## Supported File Types

### Images
- **JPEG/JPG**: Max 10MB
- **PNG**: Max 10MB
- **GIF**: Max 5MB
- **WebP**: Max 10MB
- **SVG**: Max 1MB

### Documents
- **PDF**: Max 50MB
- **Text**: Max 10MB
- **Markdown**: Max 10MB
- **JSON**: Max 10MB

### Code Files
- **Python**: Max 5MB
- **JavaScript**: Max 5MB
- **HTML**: Max 5MB
- **CSS**: Max 5MB

### Archives
- **ZIP**: Max 100MB
- **TAR**: Max 100MB

### Media
- **Audio (MP3, WAV, OGG)**: Max 50-100MB
- **Video (MP4, WebM, MOV)**: Max 500MB

## API Endpoints

### File Upload

```http
POST /api/v1/storage/upload
Content-Type: multipart/form-data

Parameters:
- file: File to upload (required)
- storage_path: Storage path type (default: user_uploads)
- user_id: User ID for user-specific paths
- project_id: Project ID for project-specific paths
- public: Make file publicly accessible (default: false)
- metadata: Additional metadata as JSON string
```

**Response:**
```json
{
  "success": true,
  "file": {
    "path": "user-uploads/123/20241206_143022_uuid.txt",
    "download_url": "https://storage.googleapis.com/...",
    "public_url": null,
    "size": 1024,
    "content_type": "text/plain",
    "uploaded_at": "2024-12-06T14:30:22Z"
  },
  "message": "File uploaded successfully"
}
```

### File Download

```http
GET /api/v1/storage/download/{file_path}

Query Parameters:
- type: Download type (inline|attachment, default: inline)
```

### File Information

```http
GET /api/v1/storage/info/{file_path}
```

**Response:**
```json
{
  "success": true,
  "file": {
    "name": "file.txt",
    "size": 1024,
    "content_type": "text/plain",
    "created": "2024-12-06T14:30:22Z",
    "updated": "2024-12-06T14:30:22Z",
    "metadata": {...},
    "public_url": "https://...",
    "md5_hash": "abc123",
    "etag": "etag123"
  }
}
```

### File Deletion

```http
DELETE /api/v1/storage/delete/{file_path}
```

### List Files

```http
GET /api/v1/storage/list

Query Parameters:
- prefix: Path prefix to filter files
- max_results: Maximum results (default: 100, max: 1000)
```

### Generate Signed URL

```http
POST /api/v1/storage/signed-url/{file_path}
Content-Type: application/json

{
  "expiration_hours": 1,
  "method": "GET"
}
```

### Copy File

```http
POST /api/v1/storage/copy
Content-Type: application/json

{
  "source_path": "source/file.txt",
  "destination_path": "dest/file.txt"
}
```

### Storage Usage

```http
GET /api/v1/storage/usage

Query Parameters:
- prefix: Path prefix to analyze
```

### Generate Upload URL

```http
POST /api/v1/storage/upload-url
Content-Type: application/json

{
  "filename": "document.pdf",
  "storage_path": "user_uploads",
  "user_id": "123",
  "expiration_hours": 1
}
```

## Usage Examples

### Basic File Upload

```python
from src.firebase_storage import get_storage_manager

manager = get_storage_manager()

# Upload file
with open('document.pdf', 'rb') as file:
    result = manager.upload_file(
        file_data=file,
        filename='document.pdf',
        storage_path='user_uploads',
        user_id='123'
    )

if result['success']:
    print(f"File uploaded: {result['download_url']}")
```

### Upload with Metadata

```python
metadata = {
    'project_name': 'AI Research',
    'tags': ['research', 'ai', 'document'],
    'author': 'John Doe'
}

result = manager.upload_file(
    file_data=file_data,
    filename='research.pdf',
    storage_path='project_files',
    project_id='proj_123',
    metadata=metadata
)
```

### Download File

```python
# Download to memory
result = manager.download_file('user-uploads/123/document.pdf')
if result['success']:
    file_data = result['file_data']

# Download to local file
result = manager.download_file(
    'user-uploads/123/document.pdf',
    local_path='/tmp/downloaded.pdf'
)
```

### Generate Signed URL

```python
# Generate download URL (valid for 2 hours)
result = manager.generate_signed_url(
    'user-uploads/123/document.pdf',
    expiration_hours=2,
    method='GET'
)

if result['success']:
    download_url = result['signed_url']
```

### List User Files

```python
# List all files for a user
result = manager.list_files('user-uploads/123/')

if result['success']:
    for file_info in result['files']:
        print(f"File: {file_info['name']}, Size: {file_info['size']}")
```

## Frontend Integration

### JavaScript Upload Example

```javascript
async function uploadFile(file, userId) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('storage_path', 'user_uploads');
    
    const response = await fetch('/api/v1/storage/upload', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('File uploaded:', result.file.download_url);
        return result.file;
    } else {
        throw new Error(result.error);
    }
}
```

### Direct Upload with Signed URL

```javascript
async function directUpload(file, userId) {
    // Get upload URL
    const urlResponse = await fetch('/api/v1/storage/upload-url', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            filename: file.name,
            storage_path: 'user_uploads',
            user_id: userId
        })
    });
    
    const urlResult = await urlResponse.json();
    
    if (urlResult.success) {
        // Upload directly to Firebase Storage
        const uploadResponse = await fetch(urlResult.upload_url, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': file.type
            }
        });
        
        if (uploadResponse.ok) {
            console.log('File uploaded directly to:', urlResult.file_path);
            return urlResult.file_path;
        }
    }
}
```

## Security Features

### File Validation

- **Type Validation**: Only allowed file types can be uploaded
- **Size Limits**: Configurable size limits per file type
- **Extension Checking**: File extensions must match content type
- **Content Scanning**: Basic content validation for security

### Access Control

- **User-based Access**: Files are organized by user ID
- **Project-based Access**: Project files are isolated
- **Signed URLs**: Time-limited access to files
- **Permission Checks**: API endpoints validate user permissions

### Security Best Practices

1. **Input Validation**: All uploads are validated before storage
2. **Secure Filenames**: Filenames are sanitized and made unique
3. **Metadata Sanitization**: User metadata is validated
4. **Access Logging**: All file operations are logged
5. **Rate Limiting**: Upload rate limits prevent abuse

## Error Handling

### Common Error Codes

- `NO_FILE`: No file provided in upload request
- `NO_FILE_SELECTED`: Empty file selected
- `UNSUPPORTED_TYPE`: File type not supported
- `FILE_TOO_LARGE`: File exceeds size limit
- `INVALID_EXTENSION`: File extension doesn't match type
- `FILE_NOT_FOUND`: Requested file doesn't exist
- `UNAUTHORIZED`: User lacks permission for operation
- `FIREBASE_ERROR`: Firebase service error
- `VALIDATION_ERROR`: File validation failed

### Error Response Format

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

## Performance Optimization

### Caching Strategy

- **CDN Integration**: Firebase Storage includes global CDN
- **Client-side Caching**: Implement browser caching for static assets
- **Signed URL Caching**: Cache signed URLs until expiration

### Upload Optimization

- **Direct Upload**: Use signed URLs for large files
- **Chunked Upload**: Implement resumable uploads for large files
- **Compression**: Compress files before upload when appropriate
- **Background Processing**: Process uploads asynchronously

### Storage Optimization

- **Lifecycle Management**: Automatically delete temporary files
- **Compression**: Store compressed versions of large files
- **Deduplication**: Avoid storing duplicate files
- **Archive Old Files**: Move old files to cheaper storage tiers

## Monitoring and Analytics

### Storage Metrics

- **Usage by User**: Track storage usage per user
- **Usage by Project**: Monitor project storage consumption
- **File Type Distribution**: Analyze uploaded file types
- **Upload/Download Patterns**: Monitor access patterns

### Performance Metrics

- **Upload Speed**: Track upload performance
- **Download Speed**: Monitor download performance
- **Error Rates**: Track operation failure rates
- **API Response Times**: Monitor endpoint performance

## Backup and Recovery

### Backup Strategy

- **Automated Backups**: Regular backups to separate storage
- **Version Control**: Keep multiple versions of important files
- **Cross-region Replication**: Replicate critical data
- **Export Functionality**: Allow users to export their data

### Recovery Procedures

- **Point-in-time Recovery**: Restore files to specific timestamps
- **Selective Recovery**: Recover specific files or folders
- **Bulk Recovery**: Restore large datasets efficiently
- **Disaster Recovery**: Complete system recovery procedures

## Integration with Aideon Features

### AI-Generated Content

- **Automatic Storage**: AI-generated files are automatically stored
- **Content Tagging**: Generated content is tagged with metadata
- **Version Tracking**: Multiple versions of generated content
- **Quality Metrics**: Store quality scores with generated files

### Project Management

- **Project Files**: All project files are organized together
- **Collaboration**: Shared access to project files
- **Version Control**: Track changes to project files
- **Export Projects**: Export entire projects with files

### User Management

- **User Quotas**: Configurable storage limits per user
- **Usage Tracking**: Monitor user storage consumption
- **Cleanup Tools**: Help users manage their storage
- **Data Export**: Allow users to export their data

## Future Enhancements

### Planned Features

1. **Advanced Search**: Full-text search within documents
2. **Image Processing**: Automatic image optimization and thumbnails
3. **Video Processing**: Video transcoding and thumbnail generation
4. **Collaboration**: Real-time collaborative editing
5. **Version Control**: Git-like version control for files

### Scalability Improvements

1. **Multi-region Storage**: Store files closer to users
2. **Edge Caching**: Cache frequently accessed files at edge locations
3. **Intelligent Tiering**: Automatically move files to appropriate storage tiers
4. **Compression**: Advanced compression algorithms for better storage efficiency

