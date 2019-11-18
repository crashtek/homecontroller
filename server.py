#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__      = "Carlos Mostek"
__credits__     = ["Carlos Mostek"]
__license__     = "MIT"
__version__     = "0.1"
__maintainer__  = "Carlos Mostek"
__email__       = "carlosmostek@gmail.com"
__status__      = "Development"

from __init__ import *
from auth.AuthService import AuthService
from auth.GettingStartedView import GettingStartedView
from blinds.Room import getRooms, ViewSchedules
from blinds.ScheduleClock import ScheduleClock
from home.Dashboard import Dashboard
from home.HomeController import HomeController

##################################################################################################################
##################################################################################################################
##################################################################################################################

#Execute the application
if __name__ == "__main__":	
	ViewSchedules.DashboardConstructor = Dashboard
	ScheduleClock(getRooms)
	homeController = HomeController()
	auth = AuthService()
	# Eventually we will want to let people log in locally with a PIN
	if (not auth.isAuthenticated()):
		view = GettingStartedView()
	else:
		view = Dashboard()
	homeController.changeView(view)
	homeController.start()

