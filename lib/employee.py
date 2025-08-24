from __init__ import CURSOR, CONN
from department import Department
# careful: avoid circular import — import Review only inside method where needed


class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept: {self.department_id}>"

    # ----------------
    # Table management
    # ----------------
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()

    # ----------------
    # Persistence
    # ----------------
    def save(self):
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, job_title, department_id):
        emp = cls(name, job_title, department_id)
        emp.save()
        return emp

    @classmethod
    def instance_from_db(cls, row):
        emp = cls.all.get(row[0])
        if emp:
            emp.name = row[1]
            emp.job_title = row[2]
            emp.department_id = row[3]
        else:
            emp = cls(row[1], row[2], row[3], row[0])
            cls.all[emp.id] = emp
        return emp

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(r) for r in rows]

    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    # ----------------
    # Relationships
    # ----------------
    def reviews(self):
        """Return all reviews belonging to this employee"""
        from review import Review   # local import to prevent circular dependency
        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Review.instance_from_db(r) for r in rows]

    def department(self):
        """Return Department object for this employee"""
        return Department.find_by_id(self.department_id)

    # -------------------
    # Property validation
    # -------------------
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._name = value
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._job_title = value
        else:
            raise ValueError("Job title must be a non-empty string")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        dept = Department.find_by_id(value)
        if dept:
            self._department_id = value
        else:
            raise ValueError("Department must exist in the departments table")
