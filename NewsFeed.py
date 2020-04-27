
# Importing the Python modules, the dependencies of the application.
import random
import os
import sys
import json
import time
import urllib.request
import subprocess
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Main algorithm.
def run():
    """The main algorithm of the program. The GUI of the NewsFeed application is
       constructed from the MainWindow class."""

    application = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(application.exec_())

# Class for the NewsFeed GUI.
class MainWindow(QMainWindow):
    """The class for the NewsFeed GUI."""

    # Class variables are created, they are used by all methods of the MainWindow class, the SearchArticlesThread class and the SaveArticlesThread class.
    """The API Key is needed to make URL requests to https://newsapi.org/"""
    APIKEY = None

    """This list contains all news sources that news articles will be collected from."""
    news_sources = []

    """This variable decides if whether the top or the latest news articles from a given news sources will be collected."""
    sort_by_var = "top"

    """These lists contain the ID's of individual news articles saved on the computer, these ID's will be used by
       the program to distinguish between which news articles to save for offline use."""
    article_list = []
    selected_articles = []

    """This variable contains the value of the progressbar."""
    progress_bar_value = 0

    """This variable contains the working directory of the application. The working directory of the application is
       identical to the directory where NewsAPI.exe is located."""
    working_directory = (os.getcwd())
    executable_directory = (working_directory + "\\" + "NewsFeed.exe")

    # The initiation method is ran once an instance of the MainWindow class is created.
    def __init__(self, parent = None):
        """The initiation/constructor method for MainWindow class. In this method the widgets are created for the NewsFeed GUI."""

        # The title and window size of the NewsAPI GUI is set.
        super(MainWindow, self).__init__()
        self.setWindowTitle("NewsFeed 1.0.0 (64-bit)")
        self.setGeometry(150, 150, 800, 500)

        """The Main Thread (GUI Thread) of the NewsFeed application displays the GUI. The Main Thread
           is connected by signals to the SearchArticlesThread and the SaveArticlesThread. These signals
           allow for the threads to communicate to the Main Thread."""

        # Instance of the SearchArticlesThread is created.
        MainWindow.SearchArticlesThread = SearchArticlesThread()

        # Signals between the Main Thread and the Search Articles Thread are created.
        self.SearchArticlesThread.display_articles_signal.connect(MainWindow.display_articles)
        self.SearchArticlesThread.clear_textbox_signal.connect(MainWindow.clear_textbox)
        self.SearchArticlesThread.update_statusbar_signal.connect(MainWindow.update_statusbar_articles_thread)
        self.SearchArticlesThread.update_progressbar_signal.connect(MainWindow.update_progressbar)
        self.SearchArticlesThread.terminate_signal.connect(MainWindow.terminate_event_handler)
        self.SearchArticlesThread.no_connection_signal.connect(MainWindow.no_internet_connection)

        # Instance of the SaveArticlesThread is created.
        MainWindow.SaveArticlesThread = SaveArticlesThread()

        # Signals between the Main Thread and the Save Articles Thread are created.
        self.SaveArticlesThread.update_statusbar_signal.connect(MainWindow.update_statusbar_save_articles_thread)
        self.SaveArticlesThread.update_progressbar_signal.connect(MainWindow.update_progressbar)
        self.SaveArticlesThread.terminate_signal.connect(MainWindow.terminate_event_handler)
        self.SaveArticlesThread.no_connection_signal.connect(MainWindow.no_internet_connection)

        # Toolbar, Buttons and widgets are created.
        MainWindow.Toolbar = self.addToolBar("Toolbar")
        MainWindow.Search_Button = QAction("Search", self)
        MainWindow.Refresh_Button = QAction("Refresh", self)
        MainWindow.Cancel_Button = QAction("Cancel", self)
        MainWindow.Save_Button = QAction("Save Articles", self)
        MainWindow.Load_Button = QAction("Load Articles", self)
        MainWindow.Filter_Button = QAction("Filter", self)
        MainWindow.Open_Config_Button = QAction("Open Config", self)
        MainWindow.Filter_Bar = QLineEdit(self)
        MainWindow.Categories = QComboBox(self)
        MainWindow.Categories.addItem("Default")
        MainWindow.Categories.addItem("All")
        MainWindow.Categories.addItem("Business")
        MainWindow.Categories.addItem("Entertainment")
        MainWindow.Categories.addItem("Gaming")
        MainWindow.Categories.addItem("Health")
        MainWindow.Categories.addItem("Music")
        MainWindow.Categories.addItem("Politics")
        MainWindow.Categories.addItem("Science")
        MainWindow.Categories.addItem("Sport")
        MainWindow.Categories.addItem("Technology")
        MainWindow.Categories.addItem("Argentina")
        MainWindow.Categories.addItem("Australia")
        MainWindow.Categories.addItem("Brazil")
        MainWindow.Categories.addItem("Canada")
        MainWindow.Categories.addItem("China")
        MainWindow.Categories.addItem("France")
        MainWindow.Categories.addItem("Germany")
        MainWindow.Categories.addItem("India")
        MainWindow.Categories.addItem("Ireland")
        MainWindow.Categories.addItem("Israel")
        MainWindow.Categories.addItem("Italy")
        MainWindow.Categories.addItem("Netherlands")
        MainWindow.Categories.addItem("Norway")
        MainWindow.Categories.addItem("Pakistan")
        MainWindow.Categories.addItem("Russia")
        MainWindow.Categories.addItem("Saudi Arabia")
        MainWindow.Categories.addItem("South Africa")
        MainWindow.Categories.addItem("Spain")
        MainWindow.Categories.addItem("Sweden")
        MainWindow.Categories.addItem("United Kingdom")
        MainWindow.Categories.addItem("United States")
        MainWindow.SortBy = QComboBox(self)
        MainWindow.SortBy.addItem("Top")
        MainWindow.SortBy.addItem("Latest")
        MainWindow.ProgressBar = QProgressBar(self)

        # Buttons and widgets are connected to their class methods.
        MainWindow.Search_Button.triggered.connect(MainWindow.search_button_handler)
        MainWindow.Refresh_Button.triggered.connect(MainWindow.refresh_event_handler)
        MainWindow.Cancel_Button.triggered.connect(MainWindow.terminate_event_handler)
        MainWindow.Save_Button.triggered.connect(MainWindow.save_button_handler)
        MainWindow.Load_Button.triggered.connect(MainWindow.load_button_handler)
        MainWindow.Filter_Button.triggered.connect(MainWindow.filter_button_handler)
        MainWindow.Open_Config_Button.triggered.connect(MainWindow.open_config_button_event_handler)
        MainWindow.Categories.activated[str].connect(MainWindow.categories_event_handler)
        MainWindow.SortBy.activated[str].connect(MainWindow.sort_by_event_handler)

        # Widgets are added to the toolbar.
        MainWindow.Toolbar.addWidget(MainWindow.Categories)
        MainWindow.Toolbar.addWidget(MainWindow.SortBy)
        MainWindow.Toolbar.addAction(MainWindow.Search_Button)
        MainWindow.Toolbar.addAction(MainWindow.Refresh_Button)
        MainWindow.Toolbar.addAction(MainWindow.Cancel_Button)
        MainWindow.Toolbar.addWidget(MainWindow.ProgressBar)
        MainWindow.Toolbar.addAction(MainWindow.Filter_Button)
        MainWindow.Toolbar.addWidget(MainWindow.Filter_Bar)
        MainWindow.Toolbar.addAction(MainWindow.Save_Button)
        MainWindow.Toolbar.addAction(MainWindow.Load_Button)
        MainWindow.Toolbar.addAction(MainWindow.Open_Config_Button)

        # Textbox is created as the CentralWidget.
        MainWindow.Textbox = QTextBrowser(self)
        self.setCentralWidget(MainWindow.Textbox)
        MainWindow.Textbox.setReadOnly(True)
        MainWindow.Textbox.setOpenExternalLinks(True)
        MainWindow.Textbox.insertHtml("<b> NewsFeed 1.0.0 (64-bit) </b>")
        MainWindow.Textbox.insertPlainText("\n")
        MainWindow.Textbox.insertHtml("<b> Prithvi R, powered by News API </b>")
        MainWindow.Textbox.insertPlainText("\n")
        MainWindow.Textbox.insertHtml("<b>" + MainWindow.executable_directory + "</b>")
        MainWindow.Textbox.insertPlainText("\n")
        MainWindow.Textbox.insertPlainText("")
        MainWindow.Textbox.insertPlainText("\n")

        # Statusbar is added.
        MainWindow.StatusBar = self.statusBar()

        # MainWindow is displayed to the screen.
        self.show()

        # Console output.
        print("=============================================")
        print("NewsFeed 1.0.0 (64-bit)")
        print("Prithvi R, powered by News API")
        print("<28/12/2017>")
        print(MainWindow.executable_directory)
        print("=============================================")

        # Configuration file is loaded.
        MainWindow.load_configuration_file()

    # Method is activated once the "Open Config" button is pressed.
    def open_config_button_event_handler():
        """This method is activated once the "Config" button is pressed. This function opens the default text editor
           on the user's system using the subprocess module to edit the configuration file."""

        print("<GUI Thread Process: Open Configuration File>")
        config_file = subprocess.Popen(["notepad.exe", (MainWindow.working_directory + "\Config.txt")])
        config_file.wait()
        MainWindow.load_configuration_file()

    # Method is activated once the "Search" button is pressed.
    def search_button_handler():
        """This method is activated once the "Search" button is pressed. This function disables all buttons
           excluding the "Cancel" button. This function also starts the SearchArticlesThread."""

        print("<GUI Thread Process: Search Articles Thread Active>")
        MainWindow.Search_Button.setEnabled(False)
        MainWindow.Refresh_Button.setEnabled(False)
        MainWindow.SortBy.setEnabled(False)
        MainWindow.Categories.setEnabled(False)
        MainWindow.Filter_Button.setEnabled(False)
        MainWindow.Save_Button.setEnabled(False)
        MainWindow.Load_Button.setEnabled(False)
        MainWindow.Open_Config_Button.setEnabled(False)
        MainWindow.SearchArticlesThread.start()

    # Method is activated once the "Save Articles" button is pressed.
    def save_button_handler():
        """This method is activated once the "Save Articles" button is pressed. This function disables all buttons
           excluding the "Cancel" button. This function also starts the SaveArticlesThread."""

        print("<GUI Thread Process: Save Articles Thread Active>")
        MainWindow.SaveArticlesThread.start()
        MainWindow.Search_Button.setEnabled(False)
        MainWindow.Refresh_Button.setEnabled(False)
        MainWindow.Categories.setEnabled(False)
        MainWindow.SortBy.setEnabled(False)
        MainWindow.Filter_Button.setEnabled(False)
        MainWindow.Save_Button.setEnabled(False)
        MainWindow.Load_Button.setEnabled(False)
        MainWindow.Open_Config_Button.setEnabled(False)

    # Method is activated once the "Load" button is pressed.
    def load_button_handler():
        """This method is activated once the "Load" button is pressed. The user enters a directory through
           a file browser, the method loads all JSON files in the choosen directory and displays the articles
           contained in the JSON files to the GUI."""

        #Console output.
        print("<GUI Thread Process: Load Articles>")

        #User inputs directory.
        try:
            directory = str(QFileDialog.getExistingDirectory())
            os.chdir(directory)
        except OSError:
            print("<GUI Thread Process: Error: No Directory Choosen>")

        #Clear textbox.
        MainWindow.clear_textbox()

        #Reset article list.
        MainWindow.article_list = []
        MainWindow.selected_articles = []

        #Articles in the current directory are displayed.
        for news_source in MainWindow.news_sources:

            # File name is defined.
            file_name = (news_source + "-" + MainWindow.sort_by_var + ".json")
            try:

                # File is opened and the data is loaded.
                json_file = open(file_name, "r")
                data = json.load(json_file)

                # Displays articles in the data to the GUI.
                for article in data:
                    MainWindow.article_list.append(article["ID"])
                    MainWindow.selected_articles.append(article["ID"])
                    MainWindow.Textbox.insertHtml("<h2>" + article["Title"] + "</h2>")
                    MainWindow.Textbox.insertPlainText("\n")

                    if article["Description"] is "":
                        pass
                    elif article["Description"] is None:
                        pass
                    else:
                        MainWindow.Textbox.insertHtml(article["Description"])
                        MainWindow.Textbox.insertPlainText("\n")

                    link = ("<a href= " + article["URL"] + ">" + article["URL"] + " </a>")
                    MainWindow.Textbox.insertHtml(link)
                    MainWindow.Textbox.insertPlainText("\n")
                    MainWindow.Textbox.insertPlainText("")
                    MainWindow.Textbox.insertPlainText("\n")

                    # File is closed.
                    json_file.close()

            # Error code.
            except:
                print("<GUI Thread Process: Error: Could Not Find " + file_name + ">")

    # Method is activated once the "Filter" button is pressed.
    def filter_button_handler():
        """Finds keywords and phrases in the news articles that are displayed to the GUI.
           This method searches through the JSON files in the current directory, it identifies
           the articles in the JSON files which contain the keyword or phrase. It then
           displays these articles to the GUI."""

        # Valid characters.
        valid_characters = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d",
                      "e", "f", "g", "h", "i", "j", "k", "i", "m", "n", "o", "p", "q",
                      "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D",
                      "E", "F", "G", "H", "I", "J", "K", "I", "M", "N", "O", "P", "Q",
                      "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "-", "!", "?", "!"
                      ":", ";", "@", ",", ".", "#", "/", ">", "<", "(", ")", "[", "]"]

        string = MainWindow.Filter_Bar.text()
        valid_string = False
        for character in string:
            if character in valid_characters:
                valid_string = True

        # The Searching algorithm.
        if valid_string is True:

            # Textbox is cleared.
            MainWindow.clear_textbox()

            # Selected articles list is reset.
            MainWindow.selected_articles = []

            print("<GUI Thread Process: Searched For: " + string + ">")
            word_found = False
            for news_source in MainWindow.news_sources:

                # File name is defined.
                file_name = (news_source + "-" + MainWindow.sort_by_var + ".json")
                try:

                    # File is opened and the data is loaded.
                    json_file = open(file_name, "r")
                    data = json.load(json_file)

                    # Keyword or phrase is found.
                    for article in data:
                        if string in article["Title"]:
                            word_found = True
                            MainWindow.selected_articles.append(article["ID"])
                        if string in article["Description"]:
                            word_found = True
                            MainWindow.selected_articles.append(article["ID"])

                    # File is closed.
                    json_file.close()

                # Error code.
                except:
                    print("<GUI Thread Process: Error: " + file_name + " Not Found>")

            # Remove duplicates in selected articles list.
            MainWindow.selected_articles = list(set(MainWindow.selected_articles))

            # Selected articles are displayed to the GUI.
            for news_source in MainWindow.news_sources:

                # File name is defined.
                file_name = (news_source + "-" + MainWindow.sort_by_var + ".json")
                try:

                    # File is opened and the data is loaded.
                    json_file = open(file_name, "r")
                    data = json.load(json_file)

                    # Contents of the news article is displayed to the GUI.
                    for article in data:

                        # Checking if the article ID is in the selected articles list.
                        if article["ID"] in MainWindow.selected_articles:

                            # Displays articles in the data to the GUI.
                            MainWindow.Textbox.insertHtml("<h2>" + article["Title"] + "</h2>")
                            MainWindow.Textbox.insertPlainText("\n")

                            if article["Description"] is "":
                                pass
                            elif article["Description"] is None:
                                pass
                            else:
                                MainWindow.Textbox.insertHtml(article["Description"])
                                MainWindow.Textbox.insertPlainText("\n")

                            link = ("<a href= " + article["URL"] + ">" + article["URL"] + " </a>")
                            MainWindow.Textbox.insertHtml(link)
                            MainWindow.Textbox.insertPlainText("\n")
                            MainWindow.Textbox.insertPlainText("")
                            MainWindow.Textbox.insertPlainText("\n")

                    # File is closed.
                    json_file.close()

                except:
                    pass

            # No results.
            if word_found is False:
                MainWindow.Textbox.insertHtml("<h2> No Results. </h2>")

        # Error code.
        else:
            print("<GUI Thread Process: Error: Invalid String>")

    # Method is activated once the "Cancel" button is pressed.
    def terminate_event_handler():
        """This method is activated once the "Cancel" button is pressed. It terminates
           all running threads, enables all buttons and resets the status bar and progress bar."""

        MainWindow.StatusBar.showMessage("")
        MainWindow.ProgressBar.setValue(0)
        MainWindow.SearchArticlesThread.terminate()
        MainWindow.SaveArticlesThread.terminate()
        MainWindow.Search_Button.setEnabled(True)
        MainWindow.Refresh_Button.setEnabled(True)
        MainWindow.Categories.setEnabled(True)
        MainWindow.SortBy.setEnabled(True)
        MainWindow.Filter_Button.setEnabled(True)
        MainWindow.Save_Button.setEnabled(True)
        MainWindow.Load_Button.setEnabled(True)
        MainWindow.Open_Config_Button.setEnabled(True)
        print("<GUI Thread Process: Thread Terminated>")

    # Method is activated once the "Refresh" button is pressed.
    def refresh_event_handler():
        """This method is activated once the "Refresh" button is pressed. This method
           loads all news articles from the JSON files of the current directory
           and displays them to the GUI."""

        print("<GUI Thread Process: Refresh>")

        # Clear textbox.
        MainWindow.clear_textbox()

        # Reset article list.
        MainWindow.article_list = []
        MainWindow.selected_articles = []

        # Articles in the current directory are displayed.
        for news_source in MainWindow.news_sources:

            # File name is defined.
            file_name = (news_source + "-" + MainWindow.sort_by_var + ".json")
            try:

                # File is opened and the data is loaded.
                json_file = open(file_name, "r")
                data = json.load(json_file)

                # News articles in the data are displayed to the GUI.
                for article in data:
                    MainWindow.article_list.append(article["ID"])
                    MainWindow.selected_articles.append(article["ID"])
                    MainWindow.Textbox.insertHtml("<h2>" + article["Title"] + "</h2>")
                    MainWindow.Textbox.insertPlainText("\n")

                    if article["Description"] is "":
                        pass
                    elif article["Description"] is None:
                        pass
                    else:
                        MainWindow.Textbox.insertHtml(article["Description"])
                        MainWindow.Textbox.insertPlainText("\n")

                    link = ("<a href= " + article["URL"] + ">" + article["URL"] + " </a>")
                    MainWindow.Textbox.insertHtml(link)
                    MainWindow.Textbox.insertPlainText("\n")
                    MainWindow.Textbox.insertPlainText("")
                    MainWindow.Textbox.insertPlainText("\n")

                    # File is closed.
                    json_file.close()

            # Error code.
            except:
                print("<GUI Thread Process: Error: " + file_name + " Not Found>")

    # Method is activated once the "SortBy" combobox is interacted with.
    def sort_by_event_handler():
        """Event handler for the SortBy combobox."""

        sort_by_string_value = (MainWindow.SortBy.currentText())
        if sort_by_string_value == "Top":
            MainWindow.sort_by_var = ("top")
        if sort_by_string_value == "Latest":
            MainWindow.sort_by_var = ("latest")
        print("<GUI Thread Process: " + sort_by_string_value + " Selected>")

    # Method is activated once the "Country" combobox is interacted with.
    def categories_event_handler():
        """Event handler for the Country combobox."""

        string_value = (MainWindow.Categories.currentText())

        if string_value == "Default":
            print("<GUI Thread Process: Default Selected>")
            MainWindow.load_configuration_file()

        if string_value == "All":
            print("<GUI Thread Process: All Selected>")
            MainWindow.news_sources = [ "abc-news", "abc-news-au", "al-jazeera-english", "aftenposten", "ansa", "argaam", "ars-technica", "ary-news", "associated-press",
                                        "australian-financial-review", "axios", "bbc-news", "bbc-sport", "bild", "blasting-news-br", "bleacher-report", "bloomberg",
                                        "breitbart-news", "business-insider", "business-insider-uk", "buzzfeed", "cbc-news", "cbs-news", "cnbc", "cnn", "cnn-es",
                                        "crypto-coins-news", "daily-mail", "der-tagesspiegel", "die-zeit", "el-mundo", "engadget", "entertainment-weekly", "espn",
                                        "espn-cric-info", "financial-post", "financial-times", "focus", "football-italia", "fortune", "four-four-two", "fox-news",
                                        "fox-sports", "globo", "google-news", "google-news-ar", "google-news-au", "google-news-br", "google-news-ca", "google-news-ca",
                                        "google-news-fr", "google-news-in", "google-news-is", "google-news-it", "google-news-ru", "google-news-sa", "google-news-uk",
                                        "goteborgs-posten", "gruenderszene", "hacker-news", "handelsblatt", "ign", "il-sole-24-ore", "independent", "infobae", "info-money",
                                        "la-gaceta", "la-nacion", "la-repubblica", "le-monde", "lenta", "lequipe", "liberation", "marca", "mashable", "medical-news-today",
                                        "metro", "mirror", "msnbc", "mtv-news", "mtv-news-uk", "national-geographic", "nbc-news", "news24", "new-scientist", "news-com-au",
                                        "newsweek", "new-york-magazine", "next-big-future", "nfl-news", "nhl-news", "nrk", "politico", "polygon", "rbc", "recode",
                                        "reuters", "rt", "rte", "rtl-nieuws", "sabq", "spiegel-online", "svenska-dagbladet", "t3n", "talksport", "techcrunch",
                                        "techcrunch-cn", "techradar", "the-economist","the-guardian-au", "the-guardian-uk", "the-hill", "the-hindu", "the-huffington-post",
                                        "the-irish-times", "the-lad-bible", "the-new-york-times", "the-next-web", "the-sport-bible", "the-telegraph", "the-times-of-india",
                                        "the-verge","the-next-web", "the-sport-bible","the-telegraph","the-times-of-india", "the-verge", "the-wall-street-journal", "the-washington-post",
                                        "time", "usa-today", "vice-news", "wired-de", "wirtschafts-woche", "xinhua-net", "ynet"]

        if string_value == "Business":
            print("<GUI Thread Process: Business Selected>")
            MainWindow.news_sources = ["bloomberg", "australian-financial-review", "bloomberg", "business-insider", "business-insider-uk",
                                        "cnbc", "die-zeit", "financial-post", "financial-times", "fortune", "handelsblatt", "il-sole-24-ore",
                                        "info-money", "les-echos", "the-economist", "the-wall-street-journal", "wirtschafts-woche"]

        if string_value == "Entertainment":
            print("<GUI Thread Process: Entertainment Selected>")
            MainWindow.news_sources = ["buzzfeed", "daily-mail", "entertainment-weekly", "mashable", "the-lad-bible"]

        if string_value == "Gaming":
            print("<GUI Thread Process: Gaming Selected>")
            MainWindow.news_sources = ["ign", "polygon"]

        if string_value == "Health":
            print("<GUI Thread Process: Health Selected>")
            MainWindow.news_sources = ["medical-news-today"]

        if string_value == "Music":
            print("<GUI Thread Process: Music Selected>")
            MainWindow.news_sources = ["mtv-news", "mtv-news-uk"]

        if string_value == "Politics":
            print("<GUI Thread Process: Politics Selected>")
            MainWindow.news_sources = ["breitbart-news", "la-nacion", "politico", "the-hill"]

        if string_value == "Science":
            print("<GUI Thread Process: Science Selected>")
            MainWindow.news_sources = ["national-geographic", "new-scientist", "next-big-future"]

        if string_value == "Sport":
            print("<GUI Thread Process: Sport Selected>")
            MainWindow.news_sources = ["bbc-sport", "bleacher-report", "espn", "football-italia", "four-four-two",
                                       "fox-sports", "lequip", "marca", "nfl-news", "nhl-news", "talksport", "the-sport-bible"]

        if string_value == "Technology":
            print("<GUI Thread Process: Technology Selected>")
            MainWindow.news_sources = ["gruenderszene", "hacker-news", "recode", "t3n", "techcrunch", "techradar", "the-next-web",
                                       "the-verge", "wired", "wired-de"]

        if string_value == "Argentina":
            print("<GUI Thread Process: Argentina Selected>")
            MainWindow.news_sources = ["infobae", "la-gaceta", "la-nacion"]

        if string_value == "Australia":
            print("<GUI Thread Process: Australia Selected>")
            MainWindow.news_sources = ["abc-news-au", "australian-financial-review", "google-news-au", "news-com-au", "the-guardian-au"]

        if string_value == "Brazil":
            print("<GUI Thread Process: Brazil Selected>")
            MainWindow.news_sources = ["blasting-news-br", "globo", "google-news-br", "info-money"]

        if string_value == "Canada":
            print("<GUI Thread Process: Canada Selected>")
            MainWindow.news_sources = ["cbc-news", "financial-post", "google-news-ca", "the-globe-and-mail"]

        if string_value == "China":
            print("<GUI Thread Process: China Selected>")
            MainWindow.news_sources = ["techcrunch-cn", "xinhua-net"]

        if string_value == "France":
            print("<GUI Thread Process: France Selected>")
            MainWindow.news_sources = ["google-news-fr", "le-monde", "lequip", "les-echos", "liberation"]

        if string_value == "Germany":
            print("<GUI Thread Process: Germany Selected>")
            MainWindow.news_sources = ["bild", "der-tagesspiegel", "die-zeit", "focus", "gruenderszene", "handelsblatt", "spiegel-online", "t3n", "wired-de", "wirtschafts-woche"]

        if string_value == "India":
            print("<GUI Thread Process: India Selected>")
            MainWindow.news_sources = ["google-news-in", "the-hindu", "the-times-of-india"]

        if string_value == "Ireland":
            print("<GUI Thread Process: Ireland Selected>")
            MainWindow.news_sources = ["rte", "the-irish-times"]

        if string_value == "Israel":
            print("<GUI Thread Process: Israel Selected>")
            MainWindow.news_sources = ["google-news-is", "ynet"]

        if string_value == "Italy":
            print("<GUI Thread Process: Italy Selected>")
            MainWindow.news_sources = ["ansa", "football-italia", "google-news-it", "il-sole-24-ore", "la-repubblica"]

        if string_value == "Netherlands":
            print("<GUI Thread Process: Netherlands Selected>")
            MainWindow.news_sources = ["rtl-nieuws"]

        if string_value == "Norway":
            print("<GUI Thread Process: Norway Selected>")
            MainWindow.news_sources = ["aftenposten", "nrk"]

        if string_value == "Pakistan":
            print("<GUI Thread Process: Pakistan Selected>")
            MainWindow.news_sources = ["ary-news"]

        if string_value == "Russia":
            print("<GUI Thread Process: Russia Selected>")
            MainWindow.news_sources = ["google-news-ru", "lenta", "rbc", "rt"]

        if string_value == "Saudi Arabia":
            print("<GUI Thread Process: Saudi Arabia Selected>")
            MainWindow.news_sources = ["argaam", "google-news-sa", "sabq"]

        if string_value == "South Africa":
            print("<GUI Thread Process: South Africa Selected>")
            MainWindow.news_sources = ["news24"]

        if string_value == "Spain":
            print("<GUI Thread Process: Spain Selected>")
            MainWindow.news_sources = ["el-mundo", "marca"]

        if string_value == "Sweden":
            print("<GUI Thread Process: Sweden Selected>")
            MainWindow.news_sources = ["goteborgs-posten", "svenska-dagbladet"]

        if string_value == "United Kingdom":
            print("<GUI Thread Process: United Kingdom Selected>")
            MainWindow.news_sources = ["bbc-news", "bbc-sport", "business-insider", "daily-mail",
                                       "financial-times", "four-four-two", "google-news-uk", "independent",
                                       "metro", "mirror", "mtv-news-uk", "talksport", "the-economist",
                                       "the-guardian-uk", "the-lad-bible", "the-sport-bible", "the-telegraph"]

        if string_value == "United States":
            print("<GUI Thread Process: United States Selected>")
            MainWindow.news_sources = ["abc-news", "associated-press", "axios", "bleacher-report", "bloomberg",
                                       "breitbart-news", "business-insider", "cbs-news", "cnbc", "cnn", "espn",
                                       "fortune", "fox-news", "google-news","msnbc", "mtv-news", "national-geographic",
                                       "nbc-news", "new-york-magazine", "nfl-news", "polygon", "reuters", "time",
                                       "usa-today", "the-washington-post", "wired", "the-new-york-times"]

    # Method is used to load the information from Config.txt.
    def load_configuration_file():
        """This method loads the Config.txt file. The news sources and API key is
           loaded from the configuration file (Config.txt)."""

        try:
            #Configuration file is opened and loaded.
            configuration_file = open((MainWindow.working_directory + "\Config.txt"), "r")
            file_data = configuration_file.read()
            file_data = eval(file_data)
            MainWindow.APIKEY = (file_data["APIKEY"])
            MainWindow.news_sources = (file_data["Sources"])
            print("<GUI Thread Process: Configuration File Loaded>")
            configuration_file.close()

        except:
            # Configuration file is created and loaded.
            configuration_file = open((MainWindow.working_directory + "\Config.txt"), "w")
            configuration_file.write("{'Sources': ['bbc-news', 'daily-mail', 'cnn', 'mirror'], 'APIKEY': ''}")
            configuration_file = open("Config.txt", "r")
            file_data = configuration_file.read()
            file_data = eval(file_data)
            MainWindow.APIKEY = (file_data["APIKEY"])
            MainWindow.news_sources = (file_data["Sources"])
            print("<GUI Thread Process: Configuration File Created>")
            configuration_file.close()

        # API Key from the configuration file is checked.
        if MainWindow.APIKEY == "":
            print("<GUI Thread Process: Error: API Key Missing>")
            warning_box = QMessageBox()
            warning_box.setIcon(QMessageBox.Critical)
            warning_box.setWindowTitle("No API Key")
            warning_box.setText("Requests cannot be made to News API without an API key.")
            warning_box.exec_()

    # Method is used to display articles to the GUI.
    def display_articles():
        """This method loads JSON files from the current directorty and displays the articles
           stored in the JSON files."""

        print("<GUI Thread Process: Display Articles>")

        # Selected articles are displayed to the GUI.
        for news_source in MainWindow.news_sources:

            # File name is defined.
            file_name = (news_source + "-" + MainWindow.sort_by_var + ".json")
            try:

                # File is opened and the data is loaded.
                json_file = open(file_name, "r")
                data = json.load(json_file)

                # Displays articles in the data to the GUI.
                for article in data:
                    MainWindow.article_list.append(article["ID"])
                    MainWindow.selected_articles.append(article["ID"])
                    MainWindow.Textbox.insertHtml("<h2>" + article["Title"] + "</h2>")
                    MainWindow.Textbox.insertPlainText("\n")

                    if article["Description"] is "":
                        pass
                    elif article["Description"] is None:
                        pass
                    else:
                        MainWindow.Textbox.insertHtml(article["Description"])
                        MainWindow.Textbox.insertPlainText("\n")

                    Link = ("<a href= " + article["URL"] + ">" + article["URL"] + " </a>")
                    MainWindow.Textbox.insertHtml(Link)
                    MainWindow.Textbox.insertPlainText("\n")
                    MainWindow.Textbox.insertPlainText("")
                    MainWindow.Textbox.insertPlainText("\n")

                    # File is closed.
                    json_file.close()

            # Error code.
            except:
                print("<GUI Thread Process: Error: " + file_name + " Not Found>")

    # Method is used to display a warning box when there is no internet connection.
    def no_internet_connection():
        """This method displays a warning box when there is no internet connection."""

        print("<GUI Thread Process: No Internet Connection>")
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Critical)
        warning_box.setWindowTitle("No Internet Connection")
        warning_box.setText("Could not connect to News API")
        warning_box.exec_()

    # Method is used to create unique ID's for all articles.
    def create_article_id():
        """This method is used to create unique ID's for all articles."""

        characters = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d",
                      "e", "f", "g", "h", "i", "j", "k", "i", "m", "n", "o", "p", "q",
                      "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D",
                      "E", "F", "G", "H", "I", "J", "K", "I", "M", "N", "O", "P", "Q",
                      "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

        article_id = []
        for interations in range(10):
            article_id.append(random.choice(characters))
        article_id = (''.join(article_id))
        return article_id

    # Method is used to clear all text from the GUI.
    def clear_textbox():
        """This method clears all text from the text box."""

        MainWindow.Textbox.clear()
        MainWindow.Textbox.insertHtml("<b> NewsFeed 1.0.0 (64-bit) </b>")
        MainWindow.Textbox.insertPlainText("\n")
        MainWindow.Textbox.insertHtml("<b> Prithvi R, powered by News API </b>")
        MainWindow.Textbox.insertPlainText("\n")
        MainWindow.Textbox.insertHtml("<b>" + MainWindow.executable_directory + "</b>")
        MainWindow.Textbox.insertPlainText("\n")
        MainWindow.Textbox.insertPlainText("")
        MainWindow.Textbox.insertPlainText("\n")

    # Method is used to update the statusbar.
    def update_statusbar_articles_thread():
        """This method updates the statusbar. (Search Articles Thread)"""

        MainWindow.StatusBar.showMessage("Collecting " + MainWindow.sort_by_var.capitalize() + " Articles...")

    # Method is used update the statusbar.
    def update_statusbar_save_articles_thread():
        """This method updates the statusbar (Save Articles Thread)"""

        MainWindow.StatusBar.showMessage("Saving Articles Offline...")

    # Method is used to update the progressbar.
    def update_progressbar():
        """This method updates the statusbar."""

        MainWindow.ProgressBar.setValue(MainWindow.progress_bar_value)

# Class for the Search Articles Thread.
class SearchArticlesThread(QThread):
    """The SearchArticlesThread searches for news articles."""

    # Defining signals.
    clear_textbox_signal = pyqtSignal()
    update_statusbar_signal = pyqtSignal()
    update_progressbar_signal = pyqtSignal()
    display_articles_signal = pyqtSignal()
    terminate_signal = pyqtSignal()
    no_connection_signal = pyqtSignal()

    def __init__(self, parent = None):
        super(SearchArticlesThread, self).__init__(parent)

    def __del__(self):
        self.wait()

    def run(self):
        """This method of the SearchArticlesThread contains the algorithm for searching for news articles."""

        #Checking internet connection.
        try:
            print("<Info: Attempting Connection With https://newsapi.org>")
            urllib.request.urlopen("https://newsapi.org/")
            print ("<Search Articles Thread Process: Connected To NewsAPI.org>")
        except:
            self.no_connection_signal.emit()

        # Articles lists reset.
        MainWindow.article_list = []
        MainWindow.selected_articles = []

        # Texbox cleared.
        self.clear_textbox_signal.emit()

        # Calculated values for the progressbar.
        number_of_sources = 0
        for news_source in MainWindow.news_sources:
            number_of_sources = number_of_sources + 1
            divident = 100 / number_of_sources
        print("<Info: Collecting News Articles From " + str(number_of_sources) + " Source(s)>")

        # Updating statusbar.
        self.update_statusbar_signal.emit()

        # Find the date.
        raw_time = time.asctime()
        raw_time = raw_time.split()
        day = raw_time[2]
        month = raw_time[1]
        year = raw_time[4]
        date = str(day + month + year)

        # Reset Directory.
        os.chdir(MainWindow.working_directory)

        # Directory archive created.
        try:
            os.mkdir("Archive")
            os.chdir("Archive")
            os.mkdir(date)
            os.chdir(date)
        except:
            try:
                os.chdir("Archive")
                os.mkdir(date)
                os.chdir(date)
            except:
                os.chdir(date)

        # Algorithm for collecting news articles.
        completed = 0
        for news_source in MainWindow.news_sources:
            try:
                if MainWindow.sort_by_var == "top":
                    sort_by = "top-headlines?"
                if MainWindow.sort_by_var == "latest":
                    sort_by = "everything?"

                #URL request is created.
                url = ("https://newsapi.org/v2/" + sort_by + "sources=" + news_source + "&apiKey=" + MainWindow.APIKEY)

                #URL address is opened, returning JSON data from NewsAPI.org.
                server_response = (json.load(urllib.request.urlopen(url)))

            except:
                server_response = None
                print("<Search Articles Thread Process: Error: Data Not Collected For: " + news_source + "-" + MainWindow.sort_by_var + ">")

            #The news articles from NewsAPI.org is formatted and saved.
            try:
                formatted_articles = []
                for article in server_response["articles"]:

                    #Unique ID is created for each news article.
                    article_id = MainWindow.create_article_id()

                    # Formatting algorithm.
                    author = article["author"]
                    published = article["publishedAt"]
                    title = article["title"]
                    description = article["description"]
                    url = article["url"]
                    formatted_article = {"ID": (article_id), "Title": (title), "Description": (description), "Author": (author), "Published": (published), "URL": (url)}
                    formatted_articles.append(formatted_article)
                    MainWindow.article_list.append(article_id)

                # JSON file containing news articles for a given source is saved.
                formatted_data = (json.dumps(formatted_articles, indent=4, sort_keys = False))
                json_file = open(news_source + "-" + MainWindow.sort_by_var + ".json", "w")
                json_file.write(formatted_data)
                json_file.close()

                # StatusBar is updated.
                completed = completed + divident
                MainWindow.progress_bar_value = completed
                self.update_progressbar_signal.emit()
                print("<Search Articles Thread Process: JSON Created For: " + news_source + "-" + MainWindow.sort_by_var + ">" + " <" + str(int(completed)) + "%" + ">")

            #Error code.
            except:
                print("<Search Articles Thread Process: JSON Not Created For: " + news_source + "-" + MainWindow.sort_by_var + ">")

        # Selected articles updated.
        MainWindow.selected_articles = MainWindow.article_list

        # Signal sent to display news articles to GUI.
        self.display_articles_signal.emit()

        #Number of articles is calculated.
        try:
            for number_of_articles, article in enumerate(MainWindow.article_list, 1):
                pass
            print("<Info: " + str(number_of_articles) + " Articles Collected>")
        except:
            print("<Search Articles Thread Process: Error: No Articles Collected>")

        # Signal sent to terminate thread.
        self.terminate_signal.emit()

# Class for the Save Articles Thread.
class SaveArticlesThread(QThread):
    """The SaveArticlesThread saves news articles offline as HTML files."""

    # Defining signals.
    update_statusbar_signal = pyqtSignal()
    update_progressbar_signal = pyqtSignal()
    terminate_signal = pyqtSignal()
    no_connection_signal = pyqtSignal()

    def __init__(self, parent = None):
        super(SaveArticlesThread, self).__init__(parent)

    def __del__(self):
        self.wait()

    def run(self):
        """This method of the SaveArticlesThread contains the algorithm for saving news articles offline."""

        #Number of articles is calculated.
        try:
            for number_of_articles, article in enumerate(MainWindow.selected_articles, 1):
                pass
            print("<Info: Preparing To Save " + str(number_of_articles) + " Article(s)>")
        except:
            print("<Save Articles Thread Process: Error: No Articles>")

        #Calculating values for progressbar.
        try:
            divident = 100 / number_of_articles
        except:
            self.terminate_signal.emit()

        # Internet connection is checked.
        try:
            print("<Info: Attempting Connection With https://newsapi.org>")
            urllib.request.urlopen("https://newsapi.org")
            print("<Save Articles Thread Process: Connected To NewsAPI.org>")
        except:
            self.no_connection_signal.emit()

        # Statusbar is updated.
        self.update_statusbar_signal.emit()

        # Saving algorithm.
        completed = 0
        for news_source in MainWindow.news_sources:
            try:
                file_name = (news_source + "-" + MainWindow.sort_by_var + ".json")
                json_file = open(file_name, "r")
                article_list = json.load(json_file)

                for article in article_list:
                    # Checking if the article ID is in the selected articles list.
                    if article["ID"] in MainWindow.selected_articles:

                        # Article is saved for offline use.
                        print("<Save Articles Thread Process: Parsing ID: " + article["ID"] + ">")
                        web_page = urllib.request.urlopen(article["URL"])
                        soup = BeautifulSoup(web_page, "html.parser")
                        soup = str(soup)
                        save_file_name = (article["Title"] + ".html")
                        save_file = open(save_file_name, "w")
                        save_file.write(soup)

                        # Files are closed.
                        save_file.close()
                        json_file.close()

                        # Progressbar is updated.
                        completed = completed + divident
                        MainWindow.progress_bar_value = completed
                        self.update_progressbar_signal.emit()
                        print("<Save Articles Thread Process: Article Saved Offline: " + article["Title"] + ">" + " <" + str(int(completed)) + "%>")

            # Error code.
            except:
                completed = completed + divident
                MainWindow.progress_bar_value = completed
                self.update_progressbar_signal.emit()
                print("<Save Articles Thread Process: Error: Could Not Save Article: " + article["Title"] + ">")

        # Terminate signal is sent.
        self.terminate_signal.emit()

run()
