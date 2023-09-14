# Free-Tasks-Manager-2023

> _A free-to-use task manager developed by Joshua Lim for his 2023 NJC Computing Flask Web App Project_

# Documentation

## [Landing Page](http://tasks.joshualimzk.com:5000/)

The user is first sent to the landing page at the index page of the website if they are not logged in.

If they are logged in, the user is redirected to the tasks page.

They can access 3 pages, signup, login and admin by clicking on the buttons.

## [Signup Page](http://tasks.joshualimzk.com:5000/signup)

The user is able to create a new account on this page.

The input will be validated to make sure that the username that the user inputs has not been taken and that the password and confirmation is the same. Any error is shown to the user.

Their account infomation is saved into the database once their input is validated.

## [Login Page](http://tasks.joshualimzk.com:5000/login)

The user is able to log into an existing account on this page.

The input will be validated to make sure that their username corresponds to the correct password. Any error is shown to the user.

Their logged in state is saved by the browser until they log out.

## [Tasks Page](http://tasks.joshualimzk.com:5000/tasks/)

The user is able to view all their tasks and its due date on this page.

The user can strikeout their tasks as complete by selecting the left-most checkbox.

The user can delete their tasks by clicking the corresponding bin button.

The user can view more information and edit their tasks by clicking the corresponding edit button.

The user can add more tasks by clicking the "add task" button at the bottom of the page.

The user can log out by clicking the "logout" button at the bottom of the page.

## Edit/Details Page

After a task's edit button is selected, they are taken to an edit and details page.

The user will be able to view and edit the title and due date of the task and view the corresponding image.

The user is also able to upload a new image for the task.

Click on the "update" button to edit the details of the tasks and click on "cancel" to prevent any changes from occuring.

## [Admin Login Page](http://tasks.joshualimzk.com:5000/admin)

The Admin will be able to log in through this page. The username is `admin` and password is `admin`.

After a successful login, the admin will be sent to the admin panel.

## [Admin Panel Page](http://tasks.joshualimzk.com:5000/admin/panel)

The Admin will be able to delete any existing users from the database through this page by selecting the "bin" button.
