from . import start, help, form, tasks, feedback, menu, faq, admin

all_routers = [
    start.router,
    help.router,
    form.router,
    tasks.router,
    feedback.router,
    menu.router,
    faq.router,
    admin.router,
]