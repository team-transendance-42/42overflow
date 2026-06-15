*This project has been created as part of the 42 curriculum by diwang, eandela, pekatsar, and nmattos.*

## TRANSCENDENCE - 42OVERFLOW - DESCRIPTION
	Transcendence is the final project for the Codam Core curriculum, and must be completed with a team of 4-5 people.  The goal is to simulate a professional software development team and environment, such that we build a product using a relevant tech stack as we would in the "real world."  Our goal was to recreate a version of Stack Overflow for Codam students, 42overflow. The key features include, posting a question, which can be answered, tagged, commented on. A robust profile including history of users, and an AI assist feature.

## INSTRUCTIONS
	All prerequisites include: SvelteKit, Prisma, PostgreSQL, bycrypt, better-auth, .env setup, 


## RESOURCES
	We leveraged several resources:


## TEAM INFO
	Noah (nmattos) - PO + TL + Developer
	Diane (diwang) - PM + PO + Developer
	Petra (pekatsar) - PM + PO + Developer
	Elroy (eandela) - TL + Developer
	

## PROJECT MANAGEMENT
	Tools used for PM: Trello, Google Docs
	Communication channels: TEAMS, WhatsApp, IRL
	How the team organized the work: task distribution via Trello and meetings; weekly meetings (30-60 minutes)

## TECHNICAL STACK	
	Frontend + Backend: SvelteKit
	Database: PostgreSQL
	ORM: Prisma
	Justification for major technical decisions:


## DATABASE SCHEMA


## FEATURES LIST


## MODULES
   Minor (1 PT): Custom-made design system with reusable components, including a proper color palette, typography, and icons (minimum: 10 reusable components). (DW)
   Justification: Building a real-world web application for general users, requires a user friendly and interactive front-end website; this module makes that process faster and stream-lined.  This was a fun and creative module, and experience with design and code I haven't previously implemented at Codam.
   Implementation:  There is a style sheet for the colors, typography, and icons, and from there 10 (somewhat) standard components given our 42overflow project. 
   Major (2 PT): Standard user management and authentication.
   Users can update their profile information.
   Users can upload an avatar (with a default avatar if none provided).
   Users can add other users as friends and see their online status.Users have a profile page displaying their information. (DW)
   Justification: This is a user friendly web application geared towards a user that would return to the site for information/content, etc. The behavior implies a log-in, profile, and additional information. This is a relevant part of our web app.
   Implementation: This tied in nicely with the custom-made design system, and each page was built separately (SvelteKit makes this simple with a route to the page and then consistent ways to code the FE and BE functionality for each page), e.g. log-in, sign-up, profile page, settings for logging out, and editing of the profile, etc.  In addition, there was design/UX/UI elements to be considered for the user in addition to the coding. 





   TOTAL POINT CALCULATION: 

## INDIVIDUAL CONTRIBUTIONS