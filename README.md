# 📘 Project Documentation

## 🧭 Introduction

Welcome to the documentation for **[Project Name]**. This document provides a comprehensive overview of the system's architecture, business logic, and API interaction flow. It's designed to help developers, architects, and stakeholders understand the structural and functional design of the application.

---

## 🏗️ High-Level Architecture

### 📦 Package Overview

The system follows a layered architecture, ensuring separation of concerns and maintainability. Below is a high-level package diagram illustrating the core structure:

![High-Level Architecture Diagram](path/to/high-level-architecture.png)

### 🧱 Layered Architecture

The application is organized into the following layers:

- **Presentation Layer**: Handles user interactions and API requests.
- **Business Logic Layer**: Contains core business rules and logic.
- **Data Access Layer**: Manages persistence and data operations.

### 🧩 Facade Pattern

To reduce coupling and simplify access between layers, the **Facade Pattern** is employed. It provides a unified interface to a set of interfaces in the subsystem, making the architecture more scalable and testable.

---

## 🧠 Business Logic Layer

### 🧬 Class Diagram

The core business logic is encapsulated in well-defined classes and interfaces, adhering to object-oriented principles. The class diagram below illustrates the main entities and their relationships:

![Business Logic Class Diagram](path/to/class-diagram.png)

### 📚 Entities Overview

- **EntityA**: Represents [description and role].
- **EntityB**: Handles [functionality and relationships].
- **EntityC**: Coordinates interactions between [entities/subsystems].

These components work together to enforce business rules and ensure domain integrity.

```mermaid
classDiagram
direction LR
    class User {
	    - int id
	    - datetime dateCreation
	    - datettime dateUpdate
	    - bool isAdmin
	    - UserIdentity uId
	    + makeBooking(booking)
	    + get()
	    + set()
    }
    class Host {
	    - int rating
	    + getPlaces()
	    + editPlace()
    }
    class UserIdentity {
	    - string firstName
	    - string lastName
	    - String dateOfBirth
	    - string address
	    - string phoneNumber
	    + get()
	    + set()
    }
    class Place {
	    - int Id
	    - string name
	    - string address
	    - string description
	    - int rating
	    - int capacity
	    - int pricePerNight
	    - List amenities
	    + addAmenity(amenity)
	    + getAvailability()
	    + get()
	    + set()
    }
    class Review {
	    - int id
	    - int rating
	    - string comment
	    - datetime date
	    + get()
	    + set()
    }
    class Booking {
	    - int id
	    - int guestCount
	    - int totalPrice
	    - string status
	    + get()
	    + set()
    }
    class Amenity {
	    - int id
	    - string name
	    - string description
	    - string icon
	    + get()
	    + set()
    }

    User <|-- Host
    UserIdentity --* User
    Host "1" --> "1.." Place : owns
    User "1" --> "0.." Review : leaves
    User "1" --> "0.." Booking : makes
    Review "0..1" --> "1" Booking : concerns
    Place "1" <--> "0.." Booking
    Place o-- "0.." Amenity : features
```

## 🔁 API Interaction Flow

### 📊 Sequence Diagrams

The following sequence diagrams illustrate the flow of selected API calls, demonstrating interactions between components and data movement across the system:

#### 🔍 Example: `GET /items/{id}`

![Sequence Diagram - Get Item](path/to/sequence-get-item.png)

- **Client** sends request to API Gateway.
- **Controller** delegates to the facade.
- **Facade** interacts with business logic and data layer.
- **Response** returned to the client with the item data.

#### ➕ Example: `POST /items`

![Sequence Diagram - Create Item](path/to/sequence-create-item.png)

- **Client** submits item data.
- **Validation** and **transformation** handled in the logic layer.
- **Database** updated, and confirmation returned.

---

## 🧾 Appendix

- All diagrams are located in the `docs/diagrams/` folder.
- For setup instructions, see the [Getting Started Guide](./GETTING_STARTED.md).

