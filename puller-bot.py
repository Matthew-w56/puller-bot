"""
Author: Matthew Williams
Date:   Jan-Feb 2025

	Description:

This is a script to go onto the number pulling site that is popular with people internal to Lucid Software
and pull the numbers for whoever's login information is stored at /home/ubuntu/puller-bot/credentials.txt in the
format <USERNAME>,,,<PASSWORD>.  I understand that plaintext isn't great for storing passwords, but it is
just a little site someone at lucid made this month, so I'm not too worried about it.  An example of the
credential file would be:
	myUserNameHere,,,s3cr3tP4ssw0rd!
You can also add more than one credential set (one per line) to have the bot pull numbers for all accounts.
Make sure not to have any blank lines at the beginning or end, as it slows down the bot (works just fine
though).

See the Control Center below for general built-in controls to affect the behavior of the script, such as
when the script saves away screenshots, and how the logging behaves.

	Dependencies:

Requires Playwright, and Playwright Chromium to run.
"""





import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import re
import sys
from datetime import datetime
import time
import json
import os





###################################################################################################|
#|    CONFIGURATIONS    |##########################################################################|
###################################################################################################|

# Page URL

numberPullingWebsiteURL = "https://mynumbercollection.com/"

# File Paths

runStateFilePath = "/home/ubuntu/puller-bot/resources/status.txt"
# runStengthFilePath = "/home/ubuntu/puller-bot/resources/strength.txt"
# <RUN_STATE> gets replaced with the auto-incrementing run state counter
screenshotBasePath = "/home/ubuntu/puller-bot/screenshots/<RUN_STATE>-state/"
myLogFilePath = "/home/ubuntu/puller-bot/logs/pullerBot-<RUN_STATE>.log"
credentialsFilePath = "/home/ubuntu/puller-bot/credentials.txt"

# Logging Controls

loggingLevel = logging.INFO  # All logs are info, warning, or error
doLogToConsole = True
doLogToFile = True

# Other Settings

pageLoadTimeoutInSeconds = 10

# Screenshot Flags

doInitialScreenScreenshot = False
doReadyToLogInScreenshot = False
doPostLoginScreenshot = False
doSelectingPullButtonScreenshot = False
doPostNumberPullScreenshot = True
# Error flags
doCannotGetNumbersNotReadyScreenshot = False

###################################################################################################|
#|    END CONFIGURATIONS  |########################################################################|
###################################################################################################|


# ------------------------[ Set up utilities and environment ]------------------------


# NOTE: Do not do any logging before the configuration!

# Get the run state ready
runState = -1
try:
	with open(runStateFilePath, 'r') as f:
		runState = int(f.read())
	with open(runStateFilePath, 'w') as f:
		f.write(str(runState+1))
except FileNotFoundError as e:
	print(f"Failed to get runState file!\n{e}")
	exit(1)
if runState == -1:
	print(f"Failed to get runState file! (state == -1)")
	exit(1)

# Replace the "<RUN_STATE>'s with the run state value"
screenshotBasePath = screenshotBasePath.replace("<RUN_STATE>", str(runState))
myLogFilePath = myLogFilePath.replace("<RUN_STATE>", str(runState))

# Configure logging
myLogHandlers = []
if doLogToConsole:
	myLogHandlers.append(logging.StreamHandler(sys.stdout))
if doLogToFile:
	myLogHandlers.append(logging.FileHandler(myLogFilePath))

logging.basicConfig(
	level=loggingLevel,
	format='%(asctime)s - %(levelname)s - %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
	handlers=myLogHandlers
)

# NOTE: Now we can do logging!

# Now that we can log, log the credentials filepath given
logging.info(f"Given credential file: {credentialsFilePath}")

# Pull the run strength from file
# runStrength = 1.0
# try:
# 	with open(runStrengthFilePath, 'r') as f:
# 		runStrength = float(f.read())
# except FileNotFoundError as e:
# 	logging.error(f"Failed to get run strength!\n{e}")
# 	exit(1)


# ------------------------[ Execution Helper Methods ]------------------------


def doLogIn(page, context, credParts):
	# Fill in the username and password
	page.get_by_test_id('authenticator__text-field__input-username').fill(credParts[0])
	page.get_by_test_id('authenticator__text-field__input-password').fill(credParts[1])
	logInButton = page.get_by_test_id('amplify__button')
	logInButton.focus()
	if doReadyToLogInScreenshot:
		page.screenshot(path=screenshotBasePath+"1-ready-to-log-in.png")
	
	# Click the Sign in button
	logInButton.click()
	
	# Wait for it to load, actively checking to see when we're done
	waiting = 0
	while page.get_by_text("Sign In", exact=True).is_visible():
		time.sleep(0.2)
		logging.info("-- Waiting for Sign In page to go away")
		waiting += 1
		if waiting > 5 * pageLoadTimeoutInSeconds:
			logging.error("Timed out while waiting for Sign In page to go away!")
			page.screenshot(path=screenshotBasePath+"e-timed-out-a.png")
			exit(1)
	
	while not page.get_by_text("Your Number Collection").is_visible():
		time.sleep(0.2)
		logging.info("-- Waiting for Home page to show up")
		waiting += 1
		if waiting > 5 * pageLoadTimeoutInSeconds:
			logging.error("Timed out while waiting for Home page to show up!")
			page.screenshot(path=screenshotBasePath+"e-timed-out-b.png")
			exit(1)
	
	time.sleep(1)  # Past the new user (0h0m0s) thing
	logging.info("Got to the main page!  Done logging in.")
	
	if doPostLoginScreenshot:
		page.screenshot(path=screenshotBasePath+"2-logged-in-home-page.png")


def doNumberPull(page):
	# Highlight the button and take a screenshot to verify the correct button is selected
	pullNumbersButton = page.get_by_text('Get New Numbers')
	pullNumbersButton.focus()
	if doSelectingPullButtonScreenshot:
		page.screenshot(path=screenshotBasePath+"3-selecting-pull-button.png")
	
	# Actually pull the numbers
	pullNumbersButton.click()
	
	# Wait for the number card to pull up - to confirm it worked
	waiting = 0
	while not page.get_by_text("Your New Numbers").is_visible():
		time.sleep(0.2)
		logging.info("-- Waiting for number card to show up")
		waiting += 1
		if waiting > 5 * pageLoadTimeoutInSeconds:
			logging.error("Timed out while waiting for the number card to show up!")
			page.screenshot(path=screenshotBasePath+"e-timed-out-c.png")
			exit(1)
	
	# If we want to, screenshot proof of successful number pull
	if doPostNumberPullScreenshot:
		page.screenshot(path=screenshotBasePath+"4-after-pull-numbers.png")
	
	# Done
	logging.info("Finished the actual number pulling!")


# ------------------------[ Main Method ]------------------------


if __name__ == "__main__":
	logging.info("Starting the Main method")
	
	# Read the credentials into a list
	credentialsList = []
	with open(credentialsFilePath, 'r') as f:
		credentialsList = f.read().split("\n")
	if len(credentialsList) == 0:
		logging.error("Failed to read credentials file!")
	
	for credential in credentialsList:
		credParts = credential.split(",,,")
		if len(credParts) != 2:
			logging.warning(f"Failed to get credentials from ({credential})!")
			continue
		logging.info(f"Starting credential [{credParts[0]}]")

		# Take some small change to not pull this time (per the run strength)
		# run strength of 1 means 100% chance to run.  run strength of 0.5 means
		# a 50% chance to run this credential
		# if randomFloat() > runStrength:
		# 	logging.info(f"Random chance triggered to skip this number pull for {credParts[0]}!")
		# 	continue
		# else:
		# 	logging.info("Random chance to skip this number pull not taken; Continuing..")

		with sync_playwright() as p:
			try:
				# Set up the Playwright stuff
				browser = p.chromium.launch(headless=True)
				context = browser.new_context(
					user_agent='Mozilla/5.0 Windows NT 10.0 x64 - Number Puller Bot'
				)
				page = context.new_page()
				logging.info("Browser and context initialized")

				# Go to the website
				try:
					logging.info("Going to the page now!")
					page.goto(numberPullingWebsiteURL, wait_until='networkidle')
					time.sleep(1)
					logging.info("We got to the page!")
					if doInitialScreenScreenshot:
						page.screenshot(path=screenshotBasePath+"0-initial-screen.png")
				except PlaywrightTimeout:
					logging.error("Timeout while loading page!")
					page.screenshot(path=screenshotBasePath+"e-timed-out-d.png")
					raise
				
				# Log in
				logging.info("Logging in now!")
				doLogIn(page, context, credParts)
				
				# Now that we're logged in, check to see if it is ready yet
				# Check for not ready yet
				notReadyYet = page.get_by_text("New numbers available in:").is_visible()
				if notReadyYet:
					logging.error("Account not ready for new numbers!")
					logging.info(page.get_by_text(re.compile(r"\d+h \d+m \d+s")).text_content())
					if doCannotGetNumbersNotReadyScreenshot:
						page.screenshot(path=screenshotBasePath+"e-not-ready-yet.png")
					browser.close()
					continue
				
				# If it is ready, do the pull!
				doNumberPull(page)

				# We're done!
				time.sleep(1)  # Make sure we're all good
				logging.info("Done with the script!")
				context.close()
				browser.close()
			except Exception as e:
				logging.error(f"Script failed (credential for {credParts[0]}): {str(e)}")
				continue
			
		logging.info(f"Finished credential [{credParts[0]}]")
	
	logging.info("Finished with the main method successfully!")
