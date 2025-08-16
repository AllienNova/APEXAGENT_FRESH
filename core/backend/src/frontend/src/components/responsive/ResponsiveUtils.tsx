// src/components/responsive/ResponsiveUtils.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';

// Breakpoint sizes (in pixels)
export enum Breakpoint {
  XS = 0,    // Extra small devices (phones)
  SM = 640,  // Small devices (large phones, small tablets)
  MD = 768,  // Medium devices (tablets)
  LG = 1024, // Large devices (desktops)
  XL = 1280, // Extra large devices (large desktops)
  XXL = 1536 // Extra extra large devices
}

// Device types
export enum DeviceType {
  MOBILE = 'mobile',
  TABLET = 'tablet',
  DESKTOP = 'desktop'
}

// Orientation types
export enum Orientation {
  PORTRAIT = 'portrait',
  LANDSCAPE = 'landscape'
}

// Responsive context interface
interface ResponsiveContextType {
  width: number;
  height: number;
  breakpoint: Breakpoint;
  deviceType: DeviceType;
  orientation: Orientation;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isPortrait: boolean;
  isLandscape: boolean;
}

// Create responsive context
const ResponsiveContext = createContext<ResponsiveContextType | undefined>(undefined);

// Get current breakpoint based on window width
const getBreakpoint = (width: number): Breakpoint => {
  if (width >= Breakpoint.XXL) return Breakpoint.XXL;
  if (width >= Breakpoint.XL) return Breakpoint.XL;
  if (width >= Breakpoint.LG) return Breakpoint.LG;
  if (width >= Breakpoint.MD) return Breakpoint.MD;
  if (width >= Breakpoint.SM) return Breakpoint.SM;
  return Breakpoint.XS;
};

// Get device type based on breakpoint
const getDeviceType = (breakpoint: Breakpoint): DeviceType => {
  if (breakpoint >= Breakpoint.LG) return DeviceType.DESKTOP;
  if (breakpoint >= Breakpoint.SM) return DeviceType.TABLET;
  return DeviceType.MOBILE;
};

// Get orientation based on width and height
const getOrientation = (width: number, height: number): Orientation => {
  return width >= height ? Orientation.LANDSCAPE : Orientation.PORTRAIT;
};

// Responsive provider component
export const ResponsiveProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [dimensions, setDimensions] = useState<{ width: number; height: number }>({
    width: typeof window !== 'undefined' ? window.innerWidth : Breakpoint.LG,
    height: typeof window !== 'undefined' ? window.innerHeight : 768
  });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    // Set initial dimensions
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Clean up
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const { width, height } = dimensions;
  const breakpoint = getBreakpoint(width);
  const deviceType = getDeviceType(breakpoint);
  const orientation = getOrientation(width, height);

  const value: ResponsiveContextType = {
    width,
    height,
    breakpoint,
    deviceType,
    orientation,
    isMobile: deviceType === DeviceType.MOBILE,
    isTablet: deviceType === DeviceType.TABLET,
    isDesktop: deviceType === DeviceType.DESKTOP,
    isPortrait: orientation === Orientation.PORTRAIT,
    isLandscape: orientation === Orientation.LANDSCAPE
  };

  return (
    <ResponsiveContext.Provider value={value}>
      {children}
    </ResponsiveContext.Provider>
  );
};

// Hook for using responsive context
export const useResponsive = () => {
  const context = useContext(ResponsiveContext);
  if (!context) {
    throw new Error('useResponsive must be used within a ResponsiveProvider');
  }
  return context;
};

// Responsive component that renders different content based on device type
export const Responsive: React.FC<{
  children: React.ReactNode;
  mobile?: React.ReactNode;
  tablet?: React.ReactNode;
  desktop?: React.ReactNode;
}> = ({ children, mobile, tablet, desktop }) => {
  const { deviceType } = useResponsive();

  if (deviceType === DeviceType.MOBILE && mobile !== undefined) {
    return <>{mobile}</>;
  }

  if (deviceType === DeviceType.TABLET && tablet !== undefined) {
    return <>{tablet}</>;
  }

  if (deviceType === DeviceType.DESKTOP && desktop !== undefined) {
    return <>{desktop}</>;
  }

  return <>{children}</>;
};

// Hide component based on device type
export const Hide: React.FC<{
  children: React.ReactNode;
  xs?: boolean;
  sm?: boolean;
  md?: boolean;
  lg?: boolean;
  xl?: boolean;
  xxl?: boolean;
  mobile?: boolean;
  tablet?: boolean;
  desktop?: boolean;
  portrait?: boolean;
  landscape?: boolean;
}> = ({ 
  children, 
  xs, 
  sm, 
  md, 
  lg, 
  xl, 
  xxl,
  mobile,
  tablet,
  desktop,
  portrait,
  landscape
}) => {
  const { breakpoint, deviceType, orientation } = useResponsive();

  // Check if should hide based on breakpoint
  if (
    (xs && breakpoint === Breakpoint.XS) ||
    (sm && breakpoint === Breakpoint.SM) ||
    (md && breakpoint === Breakpoint.MD) ||
    (lg && breakpoint === Breakpoint.LG) ||
    (xl && breakpoint === Breakpoint.XL) ||
    (xxl && breakpoint === Breakpoint.XXL)
  ) {
    return null;
  }

  // Check if should hide based on device type
  if (
    (mobile && deviceType === DeviceType.MOBILE) ||
    (tablet && deviceType === DeviceType.TABLET) ||
    (desktop && deviceType === DeviceType.DESKTOP)
  ) {
    return null;
  }

  // Check if should hide based on orientation
  if (
    (portrait && orientation === Orientation.PORTRAIT) ||
    (landscape && orientation === Orientation.LANDSCAPE)
  ) {
    return null;
  }

  return <>{children}</>;
};

// Show component based on device type
export const Show: React.FC<{
  children: React.ReactNode;
  xs?: boolean;
  sm?: boolean;
  md?: boolean;
  lg?: boolean;
  xl?: boolean;
  xxl?: boolean;
  mobile?: boolean;
  tablet?: boolean;
  desktop?: boolean;
  portrait?: boolean;
  landscape?: boolean;
}> = (props) => {
  const { children, ...rest } = props;
  
  // Invert all boolean props
  const invertedProps = Object.entries(rest).reduce((acc, [key, value]) => {
    acc[key] = !value;
    return acc;
  }, {} as Record<string, boolean>);
  
  return (
    <Hide {...invertedProps}>
      {children}
    </Hide>
  );
};

// Container component that adapts to screen size
export const ResponsiveContainer: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  const { breakpoint } = useResponsive();
  
  // Determine padding based on breakpoint
  let padding = 'px-4'; // Default padding for mobile
  
  if (breakpoint >= Breakpoint.SM) {
    padding = 'px-6';
  }
  
  if (breakpoint >= Breakpoint.LG) {
    padding = 'px-8';
  }
  
  return (
    <div className={`w-full mx-auto ${padding} ${className}`}>
      {children}
    </div>
  );
};

// Grid component that adapts to screen size
export const ResponsiveGrid: React.FC<{
  children: React.ReactNode;
  columns?: { xs?: number; sm?: number; md?: number; lg?: number; xl?: number; xxl?: number };
  gap?: string;
  className?: string;
}> = ({ 
  children, 
  columns = { xs: 1, sm: 2, md: 3, lg: 4, xl: 5, xxl: 6 },
  gap = 'gap-4',
  className = '' 
}) => {
  const { breakpoint } = useResponsive();
  
  // Determine number of columns based on breakpoint
  let cols = columns.xs || 1;
  
  if (breakpoint >= Breakpoint.SM && columns.sm !== undefined) {
    cols = columns.sm;
  }
  
  if (breakpoint >= Breakpoint.MD && columns.md !== undefined) {
    cols = columns.md;
  }
  
  if (breakpoint >= Breakpoint.LG && columns.lg !== undefined) {
    cols = columns.lg;
  }
  
  if (breakpoint >= Breakpoint.XL && columns.xl !== undefined) {
    cols = columns.xl;
  }
  
  if (breakpoint >= Breakpoint.XXL && columns.xxl !== undefined) {
    cols = columns.xxl;
  }
  
  return (
    <div 
      className={`grid ${gap} ${className}`}
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
    >
      {children}
    </div>
  );
};

// Example usage component
export const ResponsiveExample: React.FC = () => {
  const { 
    width, 
    height, 
    breakpoint, 
    deviceType, 
    orientation,
    isMobile,
    isTablet,
    isDesktop
  } = useResponsive();
  
  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Responsive Utilities Example</h2>
      
      <div className="mb-6 p-4 bg-card rounded-lg border border-border">
        <h3 className="font-medium mb-2">Current Device Information</h3>
        <div className="space-y-1 text-sm">
          <div>Window Size: {width}px × {height}px</div>
          <div>Breakpoint: {Breakpoint[breakpoint]}</div>
          <div>Device Type: {deviceType}</div>
          <div>Orientation: {orientation}</div>
        </div>
      </div>
      
      <div className="mb-6">
        <h3 className="font-medium mb-2">Responsive Components</h3>
        
        <Responsive
          mobile={<div className="p-4 bg-blue-100 rounded-lg">Mobile View</div>}
          tablet={<div className="p-4 bg-green-100 rounded-lg">Tablet View</div>}
          desktop={<div className="p-4 bg-purple-100 rounded-lg">Desktop View</div>}
        >
          <div className="p-4 bg-gray-100 rounded-lg">Default View</div>
        </Responsive>
      </div>
      
      <div className="mb-6">
        <h3 className="font-medium mb-2">Show/Hide Components</h3>
        
        <div className="space-y-2">
          <Show mobile>
            <div className="p-4 bg-blue-100 rounded-lg">Only visible on mobile</div>
          </Show>
          
          <Show tablet>
            <div className="p-4 bg-green-100 rounded-lg">Only visible on tablet</div>
          </Show>
          
          <Show desktop>
            <div className="p-4 bg-purple-100 rounded-lg">Only visible on desktop</div>
          </Show>
          
          <Hide mobile>
            <div className="p-4 bg-amber-100 rounded-lg">Hidden on mobile</div>
          </Hide>
        </div>
      </div>
      
      <div className="mb-6">
        <h3 className="font-medium mb-2">Responsive Grid</h3>
        
        <ResponsiveGrid 
          columns={{ xs: 1, sm: 2, md: 3, lg: 4 }}
          className="mb-4"
        >
          {[1, 2, 3, 4, 5, 6, 7, 8].map(item => (
            <div key={item} className="p-4 bg-card rounded-lg border border-border text-center">
              Item {item}
            </div>
          ))}
        </ResponsiveGrid>
      </div>
    </div>
  );
};

export default ResponsiveProvider;
