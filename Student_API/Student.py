from fastapi import FastAPI,HTTPException,status,Query #type: ignore
from pydantic import BaseModel,EmailStr #type: ignore
from typing import Optional
import json
import os

app = FastAPI()

#Pydantic Model
class Student(BaseModel):
    id : int
    name : str
    email :  EmailStr
    course : str

class UpdateFull(BaseModel):
    name: str
    email: EmailStr
    course: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None

class StudentResponse(BaseModel):
    message: str
    student: Student

#in-memory storage

def load_students():
    try:
        if os.path.exists("students.json"):
            with open("students.json","r") as file:
                return json.load(file)  
        return []
    except Exception:
        return []

def save_students(students):
    try:
        with open("students.json","w") as file:
            json.dump(students,file)
    except Exception as e:
        print(f"Error saving students: {str(e)}")

students=load_students()


# get all data
@app.get("/")

def home():
    return {"message" : "Welcome to the Student Management API page"}

#POST Add student
@app.post("/students",status_code=status.HTTP_201_CREATED ,response_model=StudentResponse)

def add_student(student:Student):

    for s in students:
        if s["id"] ==student.id:
            raise HTTPException(status_code = 400,detail = "Student ID already Exsits")
        
    students.append(student.dict())
    save_students(students)

    return {
        "message" : "Student added successfully",
        "student" : student
    }

#get all students

@app.get("/students")

def get_students():
    return {
        "count" :len(students),
        "students" : students
    }
# search
@app.get("/students/search")

def Search_students(
    name:Optional[str] = Query(None),
    course:Optional[str] = Query(None)):
    filtered_students = students
    if name:
        filtered_students = [student for student in filtered_students if name.lower() == student["name"].lower()]
    if course:
        filtered_students = [student for student in filtered_students if course.lower() == student["course"].lower()]
    if not filtered_students:
        raise HTTPException(status_code=404, detail="No students found matching this criteria")
    
    return {
        "count": len(filtered_students),
        "students": filtered_students
    }
#Get by student id
@app.get("/students/{student_id}")

def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return {
                "student" : student
            }
    raise HTTPException(status_code = 404,
                        detail ="Student not Found")

#PUT Update the Student Details
@app.put("/students/{student_id}", summary = "Update Entire Student Details" ,response_model=StudentResponse)

def update_student(student_id:int , updated_student : UpdateFull):
    for index,student in enumerate(students):
        if student["id"] == student_id:

            students[index] = {
                "id": student_id,
                "name": updated_student.name,
                "email": updated_student.email,
                "course": updated_student.course
            }
            save_students()
            return {
                "message" : "Student updated successfully",
                "student" : students[index]
            }
    raise HTTPException ( status_code =404, detail="Student not found")

#PATCH Update only specific Fields
@app.patch("/students/{student_id}",summary = "Update Specific Fields",response_model=StudentResponse)
def update_specific_fields(student_id: int, updated_data: StudentUpdate):

    for student in students:
        if student["id"] == student_id:
            if updated_data.name is not None:
                student["name"] = updated_data.name
            if updated_data.email is not None:
                student["email"] = updated_data.email
            if updated_data.course is not None:
                student["course"] = updated_data.course
            save_students()
            return {
                "message": "Student updated successfully",
                "student": student
            }
    raise HTTPException(status_code=404, detail="Student not found")

#Delete Student

@app.delete("/students/{student_id}")

def delete_student(student_id: int):
    for index,student in enumerate(students):
        if student["id"] == student_id:
            deleted_student = students.pop(index)
            save_students()
            return { 
                "message" : "Student deleted Successfully",
                "student" : deleted_student
            }
    raise HTTPException(status_code = 404, detail = "Student not found")