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

MAJOR (2PT): Advanced permissions system (EA)
MAJOR (2PT): An organzation system (EA)
MAJOR (2PT): Implement a complete RAG (PK)
MAJOR (2PT): Implement a complete LLM system interface (PK)
MINOR (1PT): Voice/speech integration for accessibility or interaction (PK)

 TOTAL POINT CALCULATION: 17 PTS

## INDIVIDUAL CONTRIBUTIONS

 ELROY
 PETRA
 DIANE - For the mandatory part, I completed the Privacy Policy and Terms of Service. I also completed the Custom Design Module and Standard user management and authentication. This includes a profile page that can be edited, an avatar photo that can be added, or a default provided, and the ability to add/remove friends, and see that person's status online. Also, the Home page, Log In, Sign In, Profile, Edit Profile, Settings, Post page. This includes most of the front-end, including small features. I created a google doc for the project as well to aid with the organization and contributed to the README.
 NOAH 