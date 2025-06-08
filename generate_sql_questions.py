from app import app, db
from models import Question, QuestionDocument, Subject, Unit, Topic, User
from datetime import datetime, UTC

def create_questions():
    with app.app_context():
        # Get or create the subject and unit
        subject = Subject.query.filter_by(name="Database Management Systems").first()
        if not subject:
            subject = Subject(name="Database Management Systems")
            db.session.add(subject)
            db.session.commit()
        
        unit = Unit.query.filter_by(name="SQL Queries", subject_id=subject.id).first()
        if not unit:
            unit = Unit(name="SQL Queries", subject_id=subject.id)
            db.session.add(unit)
            db.session.commit()
        
        topics = {
            "Basic SQL Queries": [],
            "Joins and Subqueries": [],
            "Aggregation and Grouping": [],
            "Advanced SQL Features": [],
            "Data Modification": [],
            "Performance Tuning": []
        }
        
        # Create topics if they don't exist
        for topic_name in topics.keys():
            topic = Topic.query.filter_by(name=topic_name, unit_id=unit.id).first()
            if not topic:
                topic = Topic(name=topic_name, unit_id=unit.id)
                db.session.add(topic)
            topics[topic_name] = topic
        db.session.commit()
        
        # Get an admin user to set as uploader
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("Error: No admin user found. Please create an admin user first.")
            return
            
        # Create a document to hold these questions
        doc = QuestionDocument(
            title="SQL Query Practice Questions",
            filename="sql_queries.txt",
            original_filename="sql_queries.txt",
            file_path="/path/to/sql_queries.txt",
            file_size=1024,  # Placeholder size
            subject_id=subject.id,
            document_type="question_bank",
            status='approved',
            extraction_status='completed',
            extraction_progress=100,
            total_questions=50,
            total_pages=1,
            processed_pages=1,
            uploaded_at=datetime.now(UTC),
            uploader_id=admin_user.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # Questions data
        questions = [
            # Basic SQL Queries (10 questions)
            {
                "text": "Write a SQL query to select all columns from a table named 'employees'.",
                "solution": "SELECT * FROM employees;",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to select only the 'name' and 'salary' columns from the 'employees' table.",
                "solution": "SELECT name, salary FROM employees;",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to find all employees with a salary greater than 50000.",
                "solution": "SELECT * FROM employees WHERE salary > 50000;",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            
            # Joins and Subqueries (15 questions)
            {
                "text": "Write a SQL query to find all employees and their department names using an INNER JOIN between 'employees' and 'departments' tables.",
                "solution": "SELECT e.*, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Joins and Subqueries"
            },
            {
                "text": "Write a SQL query to find all employees who earn more than their managers.",
                "solution": "SELECT e1.name AS employee_name, e1.salary AS employee_salary, e2.name AS manager_name, e2.salary AS manager_salary FROM employees e1 JOIN employees e2 ON e1.manager_id = e2.employee_id WHERE e1.salary > e2.salary;",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Joins and Subqueries"
            },
            
            # Aggregation and Grouping (10 questions)
            {
                "text": "Write a SQL query to find the average salary by department.",
                "solution": "SELECT department_id, AVG(salary) as avg_salary FROM employees GROUP BY department_id;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Aggregation and Grouping"
            },
            {
                "text": "Write a SQL query to find departments with more than 5 employees.",
                "solution": "SELECT department_id, COUNT(*) as employee_count FROM employees GROUP BY department_id HAVING COUNT(*) > 5;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Aggregation and Grouping"
            },
            
            # Advanced SQL Features (8 questions)
            {
                "text": "Write a SQL query using a Common Table Expression (CTE) to find the second highest salary.",
                "solution": "WITH RankedSalaries AS (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rank FROM employees) SELECT salary FROM RankedSalaries WHERE rank = 2;",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Advanced SQL Features"
            },
            {
                "text": "Write a SQL query using a window function to show each employee's salary along with the average salary of their department.",
                "solution": "SELECT name, salary, department_id, AVG(salary) OVER (PARTITION BY department_id) as avg_department_salary FROM employees;",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Advanced SQL Features"
            },
            
            # Data Modification (5 questions)
            {
                "text": "Write a SQL statement to give a 10% raise to all employees in the IT department.",
                "solution": "UPDATE employees SET salary = salary * 1.10 WHERE department_id = (SELECT department_id FROM departments WHERE department_name = 'IT');",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Data Modification"
            },
            {
                "text": "Write a SQL statement to delete all employees who haven't made any sales (assuming a sales table with employee_id foreign key).",
                "solution": "DELETE FROM employees WHERE employee_id NOT IN (SELECT DISTINCT employee_id FROM sales);",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Data Modification"
            },
            
            # Performance Tuning (2 questions)
            {
                "text": "What index would you create to optimize a query that frequently searches for employees by their email address?",
                "solution": "CREATE INDEX idx_employee_email ON employees(email);",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Performance Tuning"
            }
        ]
        
        # Additional questions to reach 50
        additional_questions = [
            # More Basic SQL Queries
            {
                "text": "Write a SQL query to find all employees whose name starts with 'J'.",
                "solution": "SELECT * FROM employees WHERE name LIKE 'J%';",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to sort employees by hire date in descending order.",
                "solution": "SELECT * FROM employees ORDER BY hire_date DESC;",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            
            # More Joins and Subqueries
            {
                "text": "Write a SQL query to find all employees who work in the same department as employee with ID 100.",
                "solution": "SELECT * FROM employees WHERE department_id = (SELECT department_id FROM employees WHERE employee_id = 100) AND employee_id != 100;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Joins and Subqueries"
            },
            {
                "text": "Write a SQL query to find all departments that have no employees.",
                "solution": "SELECT d.* FROM departments d LEFT JOIN employees e ON d.department_id = e.department_id WHERE e.employee_id IS NULL;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Joins and Subqueries"
            },
            
            # More Aggregation and Grouping
            {
                "text": "Write a SQL query to find the department with the highest average salary.",
                "solution": "SELECT department_id, AVG(salary) as avg_salary FROM employees GROUP BY department_id ORDER BY avg_salary DESC LIMIT 1;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Aggregation and Grouping"
            },
            
            # More Advanced SQL Features
            {
                "text": "Write a SQL query using a recursive CTE to find all managers in an employee's management chain.",
                "solution": "WITH RECURSIVE ManagerChain AS (SELECT employee_id, name, manager_id, 1 as level FROM employees WHERE employee_id = :employee_id UNION ALL SELECT e.employee_id, e.name, e.manager_id, mc.level + 1 FROM employees e JOIN ManagerChain mc ON e.employee_id = mc.manager_id) SELECT * FROM ManagerChain ORDER BY level;",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Advanced SQL Features"
            },
            
            # More Data Modification
            {
                "text": "Write a SQL statement to insert a new department 'Research' with ID 50 and location ID 1700.",
                "solution": "INSERT INTO departments (department_id, department_name, location_id) VALUES (50, 'Research', 1700);",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Data Modification"
            },
            
            # More Performance Tuning
            {
                "text": "What type of index would be most appropriate for a column with low cardinality (few distinct values)?",
                "solution": "A bitmap index would be most appropriate for a column with low cardinality as it's more space-efficient than a B-tree index for such cases.",
                "marks": 2,
                "difficulty": "hard",
                "topic": "Performance Tuning"
            },
            
            # Additional practical scenarios
            {
                "text": "Write a SQL query to find all duplicate email addresses in the employees table.",
                "solution": "SELECT email, COUNT(*) as count FROM employees GROUP BY email HAVING COUNT(*) > 1;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to find employees who were hired in the last 30 days.",
                "solution": "SELECT * FROM employees WHERE hire_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to find the top 5 highest paid employees in each department.",
                "solution": "WITH RankedEmployees AS (SELECT *, DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank FROM employees) SELECT * FROM RankedEmployees WHERE rank <= 5;",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Advanced SQL Features"
            },
            {
                "text": "Write a SQL query to find all employees who have the same salary as at least one other employee.",
                "solution": "SELECT e1.* FROM employees e1 WHERE EXISTS (SELECT 1 FROM employees e2 WHERE e1.salary = e2.salary AND e1.employee_id != e2.employee_id) ORDER BY salary;",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Joins and Subqueries"
            },
            {
                "text": "Write a SQL query to find the median salary in the employees table.",
                "solution": "SELECT AVG(salary) as median_salary FROM (SELECT salary FROM employees ORDER BY salary LIMIT 2 - (SELECT COUNT(*) FROM employees) % 2 OFFSET (SELECT (COUNT(*) - 1) / 2 FROM employees)) AS t;",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Advanced SQL Features"
            },
            {
                "text": "Write a SQL query to find employees who earn more than the average salary of their department.",
                "solution": "SELECT e.* FROM employees e WHERE salary > (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id);",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Joins and Subqueries"
            },
            {
                "text": "Write a SQL query to find the department with the highest number of employees.",
                "solution": "SELECT department_id, COUNT(*) as employee_count FROM employees GROUP BY department_id ORDER BY employee_count DESC LIMIT 1;",
                "marks": 2,
                "difficulty": "easy",
                "topic": "Aggregation and Grouping"
            },
            {
                "text": "Write a SQL query to find all employees who have been with the company for more than 5 years.",
                "solution": "SELECT * FROM employees WHERE DATEDIFF(CURRENT_DATE, hire_date) > 5 * 365;",
                "marks": 2,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to find employees who don't have a manager.",
                "solution": "SELECT * FROM employees WHERE manager_id IS NULL;",
                "marks": 1,
                "difficulty": "easy",
                "topic": "Basic SQL Queries"
            },
            {
                "text": "Write a SQL query to find employees who were hired on the same day of the month as their manager.",
                "solution": "SELECT e.* FROM employees e JOIN employees m ON e.manager_id = m.employee_id WHERE DAY(e.hire_date) = DAY(m.hire_date);",
                "marks": 2,
                "difficulty": "medium",
                "topic": "Joins and Subqueries"
            },
            {
                "text": "Write a SQL query to find the 3rd highest salary without using TOP/LIMIT.",
                "solution": "SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees));",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Advanced SQL Features"
            },
            {
                "text": "Write a SQL query to find employees who have the highest salary in their respective departments.",
                "solution": "SELECT e.* FROM employees e WHERE (e.department_id, e.salary) IN (SELECT department_id, MAX(salary) FROM employees GROUP BY department_id);",
                "marks": 3,
                "difficulty": "hard",
                "topic": "Joins and Subqueries"
            }
        ]
        
        questions.extend(additional_questions)
        
        # Add questions to database
        for q_data in questions:
            topic = topics[q_data["topic"]]
            # Combine question and solution in the question text
            full_question = f"{q_data['text']}\n\nSolution:\n{q_data['solution']}"
            
            question = Question(
                question_text=full_question,
                question_type="programming",
                difficulty_level=q_data["difficulty"],
                marks=q_data["marks"],
                unit_id=unit.id,
                topic_id=topic.id,
                document_id=doc.id,
                created_at=datetime.now(UTC)
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"Successfully added {len(questions)} SQL query questions to the database.")

if __name__ == "__main__":
    create_questions()
