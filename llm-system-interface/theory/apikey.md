The "best practice" for API keys is a two-part strategy: hide them locally and inject them remotely. Store in your .env file which is in .gitignore, and load it with a package like godotenv. Then, set the environment variable on your server or CI/CD pipeline. This way, you never accidentally commit your keys to version control, and you can easily manage them across different environments (development, staging, production).

You can use a library like godotenv to automatically load that .env file into your environment variables so os.Getenv can find it.

Install it:
go get github.com/joho/godotenv