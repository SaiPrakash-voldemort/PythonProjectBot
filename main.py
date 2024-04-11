import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")


GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")


projects = []


def send_daily_update(context):
    global projects

    for project_name in projects:
        
        gifs_response = requests.get(f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={project_name}")
        
        if gifs_response.status_code == 200:
            gifs_data = gifs_response.json().get('data', [])
            total_views = sum(gif.get('views', 0) for gif in gifs_data)
            message = f"Daily update for '{project_name}': Total views per day: {total_views}"
        else:
            message = "Failed to fetch GIFs from Giphy API."

      
        context.bot.send_message(chat_id=context.job.context, text=message)


def set_project(update, context):
    global projects
    project_name = context.args[0]
    projects.append(project_name)
    update.message.reply_text(f"Project '{project_name}' set successfully!")


def get_views(update, context):
    global projects
    project_name = context.args[0] if len(context.args) > 0 else None

    if project_name:
        if project_name in projects:
        
            gifs_response = requests.get(f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={project_name}")
            
            if gifs_response.status_code == 200:
                gifs_data = gifs_response.json().get('data', [])
                total_views = sum(gif.get('views', 0) for gif in gifs_data)
                update.message.reply_text(f"Total views for '{project_name}': {total_views}")
            else:
                update.message.reply_text("Failed to fetch GIFs from Giphy API.")
        else:
            update.message.reply_text("Project not found. Please set a valid project name.")
    else:
        update.message.reply_text("Please provide a project name.")


def list_projects(update, context):
    global projects
    if projects:
        projects_list = "\n".join(projects)
        update.message.reply_text(f"List of projects:\n{projects_list}")
    else:
        update.message.reply_text("No projects found. Use /setproject command to add projects.")
def start(update, context):
     update.message.reply_text("This bot takes project as input and it fetches Total number of views per day specific to any project and Sends Daily Update of Project Views.")

    
def help(update, context):
     update.message.reply_text("You can use the following commands:\n"
                              "/start - Start the bot\n"
                              "/setproject- To set project name you need to pass project name as argument\n"
                              "/views - returns the total views of the projects You need to pass project name as argument\n  "
                              "/listprojects - displays projects list"
                              "/help - To know commands\n")

def main():
    
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("setproject", set_project, pass_args=True))
    dp.add_handler(CommandHandler("views", get_views, pass_args=True))
    dp.add_handler(CommandHandler("listprojects", list_projects))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()

    scheduler = BackgroundScheduler()
    scheduler.start()

    updater.job_queue.run_daily(send_daily_update, datetime.time(hour=9), context=updater.bot, name='daily_update')

    updater.idle()

if __name__ == '__main__':
    main()

