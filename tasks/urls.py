from django.urls import path
from .views import (
    TasksIndex,
    CreateProjects,
    UpdateProjects,
    DeleteProjects,
    CreateAssignment,
    UpdateAssignment,
    DeleteAssignment,
    tasks,
    ar_tasks,
    taskdetail,
    sendMessage,
    progress_task
)


urlpatterns = [
    path('',TasksIndex.as_view(), name='tasks_index'),
    path('projects/',CreateProjects.as_view(), name='projects_create'),
    path('projects/<int:pk>/edit',UpdateProjects.as_view(), name='projects_update'),
    path('projects/<int:pk>/delete',DeleteProjects.as_view(), name='projects_delete'),

    path('assignment/<int:pk>/assign',CreateAssignment.as_view(), name='assign_to'),
    path('assignment/',CreateAssignment.as_view(), name='assignment_create'),
    path('assignment/<int:pk>',UpdateAssignment.as_view(), name='assignment_update'),
    path('assignmentdelete/<int:pk>/delete',DeleteAssignment.as_view(), name='assignment_delete'),

    path('tasksuser/',tasks, name='taskuser'),
    path('tasksadmin/<int:userid>',tasks, name='taskadmin'),
    path('ar_task/<int:pk>',ar_tasks, name='ar_task'),
    path('progress_task/',progress_task, name='progress_task'),

    # START CHAT
    path('<int:pk>/',taskdetail, name='taskdetail'),
    # path('', views.index, name='index'),
    # path('<str:room_name>/', views.room, name='room'),
    # END CHAT

    path('sendmessage/', sendMessage, name='sendMessage'),
]