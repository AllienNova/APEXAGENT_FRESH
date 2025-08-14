#!/bin/bash
# ApexAgent Development Scripts
# Collection of useful scripts for ApexAgent development

set -e

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
  echo -e "${BLUE}[STEP]${NC} $1"
}

# Command line argument parsing
COMMAND=$1
shift

case $COMMAND in
  # Start the development environment
  start)
    log_step "Starting development environment..."
    docker-compose up -d
    log_info "Development environment started successfully."
    log_info "Access your application at http://localhost:3000"
    ;;

  # Stop the development environment
  stop)
    log_step "Stopping development environment..."
    docker-compose down
    log_info "Development environment stopped successfully."
    ;;

  # Restart the development environment or specific service
  restart)
    SERVICE=$1
    if [ -z "$SERVICE" ]; then
      log_step "Restarting all services..."
      docker-compose restart
      log_info "All services restarted successfully."
    else
      log_step "Restarting service: $SERVICE..."
      docker-compose restart $SERVICE
      log_info "Service $SERVICE restarted successfully."
    fi
    ;;

  # View logs of all services or a specific service
  logs)
    SERVICE=$1
    if [ -z "$SERVICE" ]; then
      log_step "Showing logs for all services..."
      docker-compose logs -f
    else
      log_step "Showing logs for service: $SERVICE..."
      docker-compose logs -f $SERVICE
    fi
    ;;

  # Run tests
  test)
    TEST_PATH=$1
    log_step "Running tests..."
    if [ -z "$TEST_PATH" ]; then
      npm test
    else
      npm test -- --testPathPattern="$TEST_PATH"
    fi
    ;;

  # Run linting
  lint)
    FIX=$1
    log_step "Running linter..."
    if [ "$FIX" == "--fix" ]; then
      npm run lint -- --fix
    else
      npm run lint
    fi
    ;;

  # Format code
  format)
    log_step "Formatting code..."
    npm run format
    log_info "Code formatting completed."
    ;;

  # Generate component
  generate)
    TYPE=$1
    NAME=$2
    
    if [ -z "$TYPE" ] || [ -z "$NAME" ]; then
      log_error "Usage: ./dev.sh generate [component|service|model] NAME"
      exit 1
    fi
    
    log_step "Generating $TYPE: $NAME..."
    
    case $TYPE in
      component)
        mkdir -p src/components/$NAME
        
        # Create component file
        cat > src/components/$NAME/$NAME.js << EOF
import React from 'react';
import PropTypes from 'prop-types';
import './styles.css';

const $NAME = (props) => {
  return (
    <div className="$NAME">
      {/* Component content */}
    </div>
  );
};

$NAME.propTypes = {
  // Define prop types here
};

$NAME.defaultProps = {
  // Define default props here
};

export default $NAME;
EOF
        
        # Create styles file
        cat > src/components/$NAME/styles.css << EOF
.$NAME {
  /* Component styles */
}
EOF
        
        # Create test file
        cat > src/components/$NAME/$NAME.test.js << EOF
import React from 'react';
import { render } from '@testing-library/react';
import $NAME from './$NAME';

describe('$NAME Component', () => {
  test('renders correctly', () => {
    const { container } = render(<$NAME />);
    expect(container).toBeInTheDocument();
  });
});
EOF
        
        # Create index file
        cat > src/components/$NAME/index.js << EOF
export { default } from './$NAME';
EOF
        
        log_info "$TYPE $NAME generated successfully."
        ;;
        
      service)
        mkdir -p src/services
        
        # Create service file
        cat > src/services/${NAME}Service.js << EOF
/**
 * $NAME Service
 * Description: Service for handling $NAME related operations
 */

class ${NAME}Service {
  /**
   * Constructor
   */
  constructor() {
    this.baseUrl = process.env.API_URL || '/api';
  }

  /**
   * Get all items
   * @returns {Promise<Array>} List of items
   */
  async getAll() {
    try {
      const response = await fetch(\`\${this.baseUrl}/${NAME.toLowerCase()}s\`);
      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching ${NAME.toLowerCase()}s:', error);
      throw error;
    }
  }

  /**
   * Get item by ID
   * @param {string} id - Item ID
   * @returns {Promise<Object>} Item data
   */
  async getById(id) {
    try {
      const response = await fetch(\`\${this.baseUrl}/${NAME.toLowerCase()}s/\${id}\`);
      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }
      return await response.json();
    } catch (error) {
      console.error(\`Error fetching ${NAME.toLowerCase()} \${id}:\`, error);
      throw error;
    }
  }

  /**
   * Create new item
   * @param {Object} data - Item data
   * @returns {Promise<Object>} Created item
   */
  async create(data) {
    try {
      const response = await fetch(\`\${this.baseUrl}/${NAME.toLowerCase()}s\`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating ${NAME.toLowerCase()}:', error);
      throw error;
    }
  }

  /**
   * Update item
   * @param {string} id - Item ID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>} Updated item
   */
  async update(id, data) {
    try {
      const response = await fetch(\`\${this.baseUrl}/${NAME.toLowerCase()}s/\${id}\`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }
      return await response.json();
    } catch (error) {
      console.error(\`Error updating ${NAME.toLowerCase()} \${id}:\`, error);
      throw error;
    }
  }

  /**
   * Delete item
   * @param {string} id - Item ID
   * @returns {Promise<void>}
   */
  async delete(id) {
    try {
      const response = await fetch(\`\${this.baseUrl}/${NAME.toLowerCase()}s/\${id}\`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }
    } catch (error) {
      console.error(\`Error deleting ${NAME.toLowerCase()} \${id}:\`, error);
      throw error;
    }
  }
}

export default new ${NAME}Service();
EOF
        
        # Create test file
        cat > src/services/${NAME}Service.test.js << EOF
import ${NAME}Service from './${NAME}Service';

// Mock fetch
global.fetch = jest.fn();

describe('${NAME}Service', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('should fetch all items', async () => {
    const mockData = [{ id: '1', name: 'Test' }];
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const result = await ${NAME}Service.getAll();
    
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/${NAME.toLowerCase()}s'));
    expect(result).toEqual(mockData);
  });

  it('should fetch item by id', async () => {
    const mockData = { id: '1', name: 'Test' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const result = await ${NAME}Service.getById('1');
    
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/${NAME.toLowerCase()}s/1'));
    expect(result).toEqual(mockData);
  });

  it('should create item', async () => {
    const mockData = { name: 'New Test' };
    const mockResponse = { id: '2', ...mockData };
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await ${NAME}Service.create(mockData);
    
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/${NAME.toLowerCase()}s'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(mockData),
      })
    );
    expect(result).toEqual(mockResponse);
  });

  it('should update item', async () => {
    const mockData = { name: 'Updated Test' };
    const mockResponse = { id: '1', ...mockData };
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await ${NAME}Service.update('1', mockData);
    
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/${NAME.toLowerCase()}s/1'),
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify(mockData),
      })
    );
    expect(result).toEqual(mockResponse);
  });

  it('should delete item', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
    });

    await ${NAME}Service.delete('1');
    
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/${NAME.toLowerCase()}s/1'),
      expect.objectContaining({
        method: 'DELETE',
      })
    );
  });

  it('should handle errors', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    await expect(${NAME}Service.getById('999')).rejects.toThrow('HTTP error');
  });
});
EOF
        
        log_info "$TYPE $NAME generated successfully."
        ;;
        
      model)
        mkdir -p src/models
        
        # Create model file
        cat > src/models/${NAME}.js << EOF
/**
 * $NAME Model
 * Description: Data model for $NAME
 */

class ${NAME} {
  /**
   * Constructor
   * @param {Object} data - Initial data
   */
  constructor(data = {}) {
    this.id = data.id || null;
    this.createdAt = data.createdAt ? new Date(data.createdAt) : new Date();
    this.updatedAt = data.updatedAt ? new Date(data.updatedAt) : new Date();
    
    // Add model-specific properties here
    // Example:
    // this.name = data.name || '';
    // this.description = data.description || '';
  }

  /**
   * Validate the model
   * @returns {boolean} Is valid
   */
  isValid() {
    // Add validation logic here
    // Example:
    // return !!this.name;
    return true;
  }

  /**
   * Convert to JSON representation
   * @returns {Object} JSON object
   */
  toJSON() {
    return {
      id: this.id,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      // Add model-specific properties here
    };
  }

  /**
   * Create from JSON data
   * @param {Object} json - JSON data
   * @returns {${NAME}} Model instance
   */
  static fromJSON(json) {
    return new ${NAME}(json);
  }
}

export default ${NAME};
EOF
        
        # Create test file
        cat > src/models/${NAME}.test.js << EOF
import ${NAME} from './${NAME}';

describe('${NAME} Model', () => {
  it('should create instance with default values', () => {
    const model = new ${NAME}();
    
    expect(model.id).toBeNull();
    expect(model.createdAt).toBeInstanceOf(Date);
    expect(model.updatedAt).toBeInstanceOf(Date);
  });

  it('should create instance with provided values', () => {
    const now = new Date();
    const data = {
      id: '123',
      createdAt: now.toISOString(),
      updatedAt: now.toISOString(),
      // Add model-specific properties here
    };
    
    const model = new ${NAME}(data);
    
    expect(model.id).toBe('123');
    expect(model.createdAt).toBeInstanceOf(Date);
    expect(model.createdAt.getTime()).toBe(now.getTime());
    expect(model.updatedAt).toBeInstanceOf(Date);
    expect(model.updatedAt.getTime()).toBe(now.getTime());
  });

  it('should validate correctly', () => {
    const model = new ${NAME}();
    expect(model.isValid()).toBe(true);
    
    // Add more validation tests based on your validation logic
  });

  it('should convert to JSON correctly', () => {
    const model = new ${NAME}({ id: '123' });
    const json = model.toJSON();
    
    expect(json.id).toBe('123');
    expect(json.createdAt).toBeDefined();
    expect(json.updatedAt).toBeDefined();
  });

  it('should create from JSON correctly', () => {
    const data = {
      id: '123',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    const model = ${NAME}.fromJSON(data);
    
    expect(model).toBeInstanceOf(${NAME});
    expect(model.id).toBe('123');
  });
});
EOF
        
        log_info "$TYPE $NAME generated successfully."
        ;;
        
      *)
        log_error "Unknown type: $TYPE. Supported types: component, service, model"
        exit 1
        ;;
    esac
    ;;

  # Clean up development environment
  clean)
    log_step "Cleaning up development environment..."
    docker-compose down -v
    log_info "Removed containers, networks, and volumes."
    
    read -p "Do you want to remove node_modules as well? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      log_step "Removing node_modules..."
      rm -rf node_modules
      log_info "node_modules removed."
    fi
    
    log_info "Cleanup completed successfully."
    ;;

  # Database operations
  db)
    DB_COMMAND=$1
    
    case $DB_COMMAND in
      reset)
        log_step "Resetting database..."
        docker-compose exec db psql -U apexagent -d apexagent_dev -f /docker-entrypoint-initdb.d/init-db.sql
        log_info "Database reset successfully."
        ;;
        
      migrate)
        log_step "Running database migrations..."
        npm run db:migrate
        log_info "Database migrations completed successfully."
        ;;
        
      seed)
        log_step "Seeding database with test data..."
        npm run db:seed
        log_info "Database seeded successfully."
        ;;
        
      shell)
        log_step "Opening database shell..."
        docker-compose exec db psql -U apexagent -d apexagent_dev
        ;;
        
      *)
        log_error "Unknown db command: $DB_COMMAND. Supported commands: reset, migrate, seed, shell"
        exit 1
        ;;
    esac
    ;;

  # Show help
  help|--help|-h)
    echo -e "${GREEN}ApexAgent Development Scripts${NC}"
    echo -e "Usage: ./dev.sh COMMAND [OPTIONS]"
    echo
    echo -e "${BLUE}Commands:${NC}"
    echo -e "  ${YELLOW}start${NC}                Start development environment"
    echo -e "  ${YELLOW}stop${NC}                 Stop development environment"
    echo -e "  ${YELLOW}restart [service]${NC}    Restart all services or a specific service"
    echo -e "  ${YELLOW}logs [service]${NC}       View logs of all services or a specific service"
    echo -e "  ${YELLOW}test [path]${NC}          Run tests, optionally for a specific path"
    echo -e "  ${YELLOW}lint [--fix]${NC}         Run linter, optionally with auto-fix"
    echo -e "  ${YELLOW}format${NC}               Format code"
    echo -e "  ${YELLOW}generate TYPE NAME${NC}   Generate code (component, service, model)"
    echo -e "  ${YELLOW}clean${NC}                Clean up development environment"
    echo -e "  ${YELLOW}db COMMAND${NC}           Database operations (reset, migrate, seed, shell)"
    echo -e "  ${YELLOW}help${NC}                 Show this help message"
    echo
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  ./dev.sh start"
    echo -e "  ./dev.sh logs app"
    echo -e "  ./dev.sh generate component Button"
    echo -e "  ./dev.sh db reset"
    ;;

  # Unknown command
  *)
    log_error "Unknown command: $COMMAND"
    echo "Run './dev.sh help' for usage information."
    exit 1
    ;;
esac
