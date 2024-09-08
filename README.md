
# Document Validator System

This project is a **Document Validator System** designed to validate textual documents using customizable validation rules, store discrepancies in a MongoDB database. The system is flexible, allowing to define validation rules and process documents through templates.

## Table of Contents

- [Project Structure](#project-structure)
- [Design Patterns Used](#design-patterns-used)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Database](#database)
- [Running Tests](#running-tests)
- [Modules](#modules)
- [License](#license)

## Project Structure

```
├── config.json                  # Configuration file
├── main.py                      # Main script to run the application
├── common.py                    # Common utilities
├── db/
│   ├── db_handlers.py           # Abstract DB handler for CRUD operations
│   └── mongodb_handler.py       # MongoDB specific operations
├── templates/
│   ├── factory.py               # Template creation and management
│   └── html_table_template.py   # Template for HTML table documents
├── validation/
│   ├── doc_validator.py         # Core document validation logic
│   └── validation_rules.py      # Validation rule builder and rule definitions
└── tests/                       # Unit tests
```

### Design Patterns Used

#### 1. Template Pattern
The Template pattern is used to support different document types in the future.

- **Pros**:
  - Encourages code reuse and reduces duplication by allowing subclasses to implement field value extractions and validation rules building.
  - Improves maintainability as the document processing structure is centralized in the base class.
  - Makes the system more flexible by allowing different document types to have customized implementations.

- **Cons**:
  - Increases complexity with additional layers of inheritance.
  - Tight coupling between the base class and subclasses, as the base class controls the overall structure.
  
#### 2. Factory Pattern
The Fabric pattern is used in the `TemplateFactory` class to create templates for different document types.

- **Pros**:
  - Encapsulates the creation logic, improving maintainability and flexibility.
  - Supports the open/closed principle by allowing easy extension for new document types without modifying existing code.
  - Decouples client code from the concrete implementation of templates, making it easier to introduce new types of documents.

- **Cons**:
  - Adds complexity.

#### 3. Strategy Pattern
The Strategy pattern is used in the implementation of the `extract_field_values` function of the `Template` class, allowing different strategies to be used for extracting values from document fields.

- **Pros**:
  - Promotes flexibility by allowing different extraction strategies to be used.

#### 4. Builder Pattern
The Builder pattern is used in the `ValidationRuleBuilder` class to construct a set of necessary validation rules in a step-by-step manner.

- **Pros**:
  - Provides a clear and fluent interface for building complex validation objects.
  - Increases readability and maintainability.

- **Cons**:
  - Introduces more complexity with the need for additional builder classes.
  - Sometimes a specific sequence of validation rules is necessary.

#### 5. Chain of Responsibility Pattern
The Chain of Responsibility pattern is used in the `FieldRuleBuilder` class to pass field data through a chain of validation checks.

- **Pros**:
  - Makes it easy to add or modify validation steps without altering the other parts of the chain.
  - Supports changes to the chain of validations.

- **Cons**:
  - Can make it difficult to track the validation flow.
  - Each validation in the chain can become a single point of failure, requiring careful error handling.

#### 6. Context Object Pattern
The Context Object pattern is used in the `FieldContext` class to pass field and value information through the validations, encapsulating all the necessary data.

- **Pros**:
  - Simplifies method signatures by encapsulating all required data in a context object.
  - Promotes reusability and flexibility by passing a single object through different validation functions.
  - Allows for easier expansion, as new fields can be added to the context without altering method signatures.

- **Cons**:
  - If not carefully designed, the context object can become a "god object" that holds too much responsibility and knowledge of the system.

### Prerequisites

- Python 3.9 or higher
- MongoDB (for storing document details and corresponding discrepancies)

## Usage

To run the document validation system:

1. **MongoDB Setup**: Ensure MongoDB is running locally or on a server and update the MongoDB connection details in `config.json`.

2. **Prepare your documents**: Ensure the documents you want to validate are in a specified folder.

3. **Run the validator:**

   ```bash
   python main.py <document_folder> <--template_params>
   ```

   Example:

   ```bash
   python main.py test-data/ --N 5 --D 10Mar2020 --SUM 1000
   ```

   - `document_folder`: The folder where your documents are stored.
   - Other dynamic parameters depending on the configuration.

4. **Check Logs**: The system logs will be generated in the log file defined in `config.json`.

## Database

The application uses database parameters defined in `config.json` file. That includes the name of the database as well as collections of documents and discrepancies. 

## Running Tests

Unfortunately unit tests are not available at the moment.


## Modules

### `main.py`
- The main entry point of the application. Handles argument parsing and orchestrates document validation through the `DocumentValidator` objects.

### `db/`
- `db_handlers.py`: General database operations.
- `mongodb_handler.py`: MongoDB-specific operations, handling the storage of documents and discrepancies.

### `templates/`
- `factory.py`: Manages the document templates.
- `html_table_template.py`: Maintains the template for HTML table documents.

### `validation/`
- `doc_validator.py`: Implements the core validation logic for documents. It interacts with templates and applies validation rules.
- `validation_rules.py`: Contains the `ValidationRuleBuilder` that allows dynamic creation of validation rules.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
