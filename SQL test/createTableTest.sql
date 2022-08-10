CREATE TABLE Customers(
    CustomerID INT PRIMARY KEY,
    FirstName NVARCHAR(255),
    LastName NVARCHAR(255),
    Address NVARCHAR(255),
    PostCode NVARCHAR(255),
    DOB DATETIME
)

CREATE TABLE Products(
    ProductID INT PRIMARY KEY,
    ProductName NVARCHAR(255),
    Price DECIMAL(18,2),
)

CREAT TABLE Orders(
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    OrdeDate DATETIME,
)
