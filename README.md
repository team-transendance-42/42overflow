*This project has been created as part of the 42 curriculum by diwang, eandela, pekatsar, and nmattos.*

## TRANSCENDENCE - 42OVERFLOW - DESCRIPTION 

Transcendence is the final project for the Codam Core curriculum, and must be completed with a team of 4-5 people. The goal is to simulate a professional software development team and environment, such that we build a product using a relevant tech stack as we would in the "real world." Our goal was to recreate a version of Stack Overflow for Codam students, 42overflow. The key features include a community where users can post questions related to the 42 curriculum (additionally comment/like/upload images), and ask AI/"AI Assist", with Advanced permissions and Organzation features. Every user also has a robust profile and can follow friends, and see the online status.

## INSTRUCTIONS 

(section containing any relevant information about compilation, installation, and/or execution.)
 Step by step instructions to run the project. The app uses docker, and runs on one command - Docker Compose Up (e.g. Docker Compose up -d --build or Docker compose up --d) 
 Prerequisites include: SvelteKit, Prisma, PostgreSQL, bycrypt, better-auth, .env setup, 

## RESOURCES 

We leveraged several resources: 

https://svelte.dev/docs/kit/load https://better-auth.com/ http://better-auth.com/docs/adapters/postgresql
Description for how AI was used...

## TEAM INFO 
Noah (nmattos) - PO + TL + Developer 
Diane (diwang) - PM + PO + Developer 
Petra (pekatsar) - PM + PO + Developer 
Elroy (eandela) - TL + Developer 

## PROJECT MANAGEMENT 

Tools used for PM: Trello, Google Docs Communication channels: TEAMS, WhatsApp, IRL, Github 
How the team organized the work: task distribution via Trello and meetings; weekly meetings (30-60 minutes)

## TECHNICAL STACK 

Frontend + Backend: SvelteKit 
Database: PostgreSQL 
ORM: Prisma 
Better-auth:

Any other significant technologies or libraries Justification for major technical decisions:

## DATABASE SCHEMA
 Visual representation or description of the database structure. Tables/collections and their relationships. Key fields and data types.

## FEATURES LIST

 -AI RAG (Petra) 
 -AI LLM (Petra) 
 -AI Voice/speech integration for accessibility or interaction (Petra) 
 -Posts with comments, likes, image uploading (Diane/Noah) 
 -Editable Profile with default Avatar (Diane) 
 -Ability to follow friends and see the online status (Diane) 
 -Advanced Permissions (Elroy) 
 -Organizations (Elroy) 
 -Custom Design Modules (Diane/Noah) 
 -Real-time updates (Noah) 
 -User Interaction / chat capability (Noah)

## MODULES 

MAJOR (2PT): Use a framework for both the frontend and backend (NM)

MAJOR (2PT): Allow users to interact with other users, chat (NM)

MINOR (1PT): Use an ORM for the database (NM)

Minor (1 PT): Custom-made design system (DW)
Justification: Building a real-world web application for general users, requires a user friendly and interactive front-end website; this module makes that process faster and stream-lined. This was a fun and creative module, and experience with design and code I haven't previously implemented at Codam. Implementation: There is a style sheet for the colors, typography, and icons, and from there 10 standard components given our 42overflow project. 

Major (2 PT): Standard user management and authentication. (DW)
Users can update their profile information. Users can upload an avatar (with a default avatar if none provided). Users can add other users as friends and see their online status.Users have a profile page displaying their information.
Justification: This is a user friendly web application geared towards a user that would return to the site for information/content, etc. The behavior implies a log-in, profile, and additional information. This is a relevant part of our web app. Implementation: This tied in nicely with the custom-made design system, and each page was built separately (SvelteKit makes this simple with a route to the page and then consistent ways to code the FE and BE functionality for each page), e.g. log-in, sign-up, profile page, settings for logging out, and editing of the profile, etc. In addition, there was design/UX/UI elements to be considered for the user in addition to the coding. 

#### MAJOR (2PT): Advanced permissions system - *(Elroy)*
*The app has three site wide roles: USER, MODERATOR, and ADMIN. ADMINs can view, edit, and delete users and change user roles and moderate content by deleting posts and comments. MODERATORs can only view users and moderate content by deleting posts and comments.*\
**justification**: An open platform like ours has a risk of users posting low quality or harmful content. The roles ensure that trusted community members (MODERATORs) and staff (ADMINs) can remove inappropriate content.\
**implementation**: The permission system is implemented in the database with a Role enum (USER, MODERATOR, ADMIN). In our app MODERATORs and ADMINs will see the ability to delete posts and comments in the same way the author would. ADMINs and MODERATORs have the ability to navigate to the /users/ page where they see an overview of all users. ADMINs can edit various fields of the USERs and both ADMINs and MODERATORs can see USERs posts and comments and delete them.
#### MAJOR (2PT): An organization system - *(Elroy)*
*Users can create, edit, and delete organizations (called "Subjects" in the codebase) that act as group spaces. Each subject has MEMBER, CURATOR, and OWNER roles. Owners can edit the subject, manage members, archive it and moderate content. CURATORs can view members and moderate content. Any logged in user can discover, join, or create subjects and interact with posts within them.*\
**justification**: Subjects allow students to organize around specific projects. Keeping discussions relevant. The different roles ensure that each subject is self moderating.\
**implementation**: The system uses a Prisa Subject model with a SubjectMember table and a SubjectRole enum (MEMBER, CURATOR, OWNER). 


MAJOR (2PT): Implement a complete RAG (PK)
MAJOR (2PT): Implement a complete LLM system interface (PK)
MINOR (1PT): Voice/speech integration for accessibility or interaction (PK)

 TOTAL POINT CALCULATION: 17 PTS

## INDIVIDUAL CONTRIBUTIONS

 ELROY - I built the site's user directory and the role-based foundations the rest of the team's moderation features rely on. My two major modules were Advanced Permissions and Organizations. For Advanced Permissions, I added the Role enum (USER, MODERATOR, ADMIN) to the database and built the /users overview page with role-based visibility (admins can view/edit user details and see emails; moderators can view users and moderate content), plus the backend utilities for changing roles, soft-deleting accounts, and deleting posts/comments. For Organizations, I designed and built the "Subjects" system. the Subject/SubjectMember Prisma models with a SubjectRole enum (MEMBER, CURATOR, OWNER), the API routes for creating, editing, archiving, and subscribing/unsubscribing to subjects, the /subjects list and creation flow, the /s/[slug] subject pages with their own posts, and the manage page owners use to edit, archive, and moderate their subject (with safeguards like blocking the last owner from unsubscribing). I also wrote the database seed script that spins up an admin, moderator, and regular user with sample subjects and posts for local testing and added robots.txt to keep private/admin pages out of search engines. I documented the reasoning behind both modules in the Modules section above.
 PETRA
 DIANE - For the mandatory part, I completed the Privacy Policy and Terms of Service. I also completed the Custom Design Module and Standard user management and authentication. This includes a profile page that can be edited, an avatar photo that can be added, or a default provided, and the ability to add/remove friends, and see that person's status online. Also, the Home page, Log In, Sign In, Profile, Edit Profile, Settings, Post page. This includes most of the front-end, including small features. I created a google doc for the project as well to aid with the organization and contributed to the README.
 NOAH 