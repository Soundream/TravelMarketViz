import sys
import os
from random import randint, uniform
import json
import glob
from datetime import datetime
import re
from pathlib import Path
from tqdm import tqdm
import builtins
import math
import numpy as np  # 添加用于平滑插值

import pygame
from pygame.locals import *
import Box2D
from Box2D import *
from Box2D.b2 import *

CUSTOM_WORDS = [
    "mobile", "american", "airbnb", "china", "pandemic", "google", "sustainability", 
    "artificial intelligence", "marketing", "distribution", "blockchain", "expedia"
]

group_mapping = {
  "2010-06": {
    "Travel": [
      "travel"
    ],
    "Mobile": [
      "mobile"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Data": [
      "data"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Marketing": [
      "marketing"
    ],
    "Online": [
      "online"
    ],
    "Technology": [
      "technology"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler",
      "travellers."
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Business": [
      "business"
    ],
    "Company": [
      "company"
    ],
    "Airline Industry": [
      "American",
      "United",
      "Airlines"
    ],
    "Destinations": [
      "China",
      "India"
    ],
    "Reviews": [
      "reviews",
      "TripAdvisor"
    ],
    "Experience": [
      "experience"
    ],
    "Global Distribution": [
      "distribution",
      "global"
    ],
    "Study": [
      "report",
      "study",
      "research"
    ],
    "Sites": [
      "site",
      "websites",
      "sites"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "First": [
      "first"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Grow": [
      "growth"
    ],
    "October": [
      "October"
    ],
    "Rate": [
      "rate"
    ],
    "Award": [
      "award"
    ],
    "Events": [
      "event",
      "events"
    ],
    "History": [
      "history"
    ],
    "Emerging": [
      "emerging"
    ],
    "Tours & Activities": [
      "activities",
      "tourism"
    ],
    "Funding": [
      "funding"
    ],
    "Investments & M&A": [
      "investment"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ],
    "Photography": [
      "photo"
    ]
  },
  "2010-07": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "travelers."
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "American",
      "Airlines"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Search Engines": [
      "Google",
      "Yahoo"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Content Marketing": [
      "content marketing"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovations": [
      "innovation",
      "innovations"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Social Networks": [
      "network",
      "networks"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Stories": [
      "story",
      "stories"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investments"
    ],
    "Acquisitions": [
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynotes": [
      "keynote",
      "keynotes"
    ]
  },
  "2010-08": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor",
      "Priceline"
    ],
    "Search Engines": [
      "Google",
      "Bing"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2010-09": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2010-10": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Microsoft"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2010-11": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor",
      "travelocity"
    ],
    "Tech Companies": [
      "Google",
      "IBM"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2010-12": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "SAP"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-01": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Microsoft"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-02": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Facebook"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-03": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "IBM"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-04": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "IBM"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-05": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor",
      "airbnb"
    ],
    "Tech Companies": [
      "Google",
      "SAP"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-06": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "IBM"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-07": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Microsoft"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-08": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor",
      "Priceline"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-09": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-10": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Microsoft"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-11": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2011-12": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Facebook"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-01": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-02": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-03": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-04": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Facebook"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-05": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-06": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Facebook"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-07": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-08": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor",
      "Orbitz"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-09": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-10": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Facebook"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-11": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor",
      "TripIt"
    ],
    "Tech Companies": [
      "Google",
      "Samsung"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2012-12": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Facebook"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-01": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-02": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-03": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-04": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Yahoo"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-05": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-06": {
    "Travel": [
      "travel"
    ],
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Data": [
      "data"
    ],
    "Online": [
      "online"
    ],
    "Booking": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Technology": [
      "technology"
    ],
    "Marketing": [
      "marketing"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Travelers": [
      "travellers",
      "travelers"
    ],
    "Content": [
      "content"
    ],
    "Users": [
      "users"
    ],
    "Experience": [
      "experience"
    ],
    "Sites": [
      "site",
      "sites",
      "websites"
    ],
    "Product": [
      "product",
      "products"
    ],
    "Social Network": [
      "Facebook",
      "Twitter"
    ],
    "First": [
      "first"
    ],
    "Airline Industry": [
      "Airlines",
      "Airways"
    ],
    "Travel Companies": [
      "Expedia",
      "TripAdvisor"
    ],
    "Tech Companies": [
      "Google",
      "Apple"
    ],
    "Study": [
      "report",
      "study"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Trip Planning": [
      "trip",
      "planning"
    ],
    "Local": [
      "local"
    ],
    "Loyalty": [
      "loyalty"
    ],
    "Innovation": [
      "innovation"
    ],
    "Apps": [
      "app",
      "apps"
    ],
    "Management": [
      "management"
    ],
    "World": [
      "world"
    ],
    "International": [
      "international"
    ],
    "Point": [
      "point"
    ],
    "Communication": [
      "communication"
    ],
    "Free": [
      "free"
    ],
    "Systems": [
      "system",
      "platform"
    ],
    "Growth": [
      "growth"
    ],
    "Web": [
      "web"
    ],
    "Community": [
      "community"
    ],
    "Rate": [
      "rate"
    ],
    "Awards": [
      "award",
      "awards"
    ],
    "Events": [
      "event",
      "events"
    ],
    "Story": [
      "story"
    ],
    "Interviews": [
      "interview",
      "interviews"
    ],
    "New Ideas": [
      "ideas",
      "new"
    ],
    "Funding": [
      "funding"
    ],
    "Investments": [
      "investment",
      "investments"
    ],
    "Acquisitions": [
      "acquisition",
      "acquisitions"
    ],
    "CEO": [
      "CEO"
    ],
    "Keynote": [
      "keynote"
    ]
  },
  "2013-07": {
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Online": [
      "online"
    ],
    "Data": [
      "data",
      "information"
    ],
    "Users": [
      "users"
    ],
    "Rates": [
      "booking",
      "price",
      "help",
      "want",
      "book",
      "then",
      "available",
      "don't",
      "going",
      "good",
      "back",
      "rate",
      "offer",
      "does",
      "sales",
      "right",
      "create",
      "rates",
      "go",
      "lot",
      "able",
      "provide",
      "offering",
      "sharing",
      "access",
      "cost",
      "amount",
      "inventory",
      "getting",
      "find",
      "looking",
      "bookings",
      "less",
      "things"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Search": [
      "search"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Marketing": [
      "marketing"
    ],
    "Websites": [
      "website",
      "brand",
      "site",
      "websites",
      "brands",
      "sites"
    ],
    "Apps": [
      "app",
      "DEVICES",
      "apps",
      "internet"
    ],
    "Consumers": [
      "consumers",
      "travellers",
      "travelers",
      "consumer"
    ],
    "Experiences": [
      "experience",
      "experiences"
    ],
    "Technology": [
      "technology"
    ],
    "Product": [
      "product"
    ],
    "Flight": [
      "flight"
    ],
    "Content": [
      "content"
    ],
    "July": [
      "July",
      "July 2013",
      "launched"
    ],
    "First": [
      "first"
    ],
    "Tech Companies": [
      "google"
    ],
    "Own": [
      "own"
    ],
    "Online Travel": [
      "TripAdvisor",
      "com",
      "expedia",
      "reviews"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Tnooz": [
      "Tnooz",
      "read",
      "story"
    ],
    "Social Media #2": [
      "facebook"
    ],
    "Take": [
      "take"
    ],
    "Startups": [
      "startup",
      "funding",
      "startups"
    ],
    "System": [
      "system",
      "platform"
    ],
    "Between": [
      "between"
    ],
    "World": [
      "world"
    ],
    "Tourism": [
      "tourism"
    ],
    "Revenue": [
      "revenue"
    ],
    "Share": [
      "share"
    ],
    "Model": [
      "model"
    ],
    "Full": [
      "full"
    ],
    "Group": [
      "group"
    ],
    "Tour": [
      "tour"
    ],
    "Top": [
      "top"
    ],
    "Based": [
      "based",
      "specific"
    ],
    "Every": [
      "every"
    ],
    "Around": [
      "around"
    ],
    "Trip": [
      "trip"
    ],
    "Research": [
      "research",
      "study"
    ],
    "Work": [
      "work"
    ],
    "Products": [
      "products"
    ],
    "Results": [
      "results"
    ],
    "Design": [
      "design"
    ],
    "Strategy": [
      "strategy"
    ],
    "Across": [
      "across",
      "various"
    ],
    "Local": [
      "local"
    ],
    "Another": [
      "another"
    ],
    "Point": [
      "point",
      "look"
    ],
    "Currently": [
      "currently",
      "already"
    ],
    "My": [
      "my"
    ],
    "Growth": [
      "growth"
    ],
    "News": [
      "news"
    ],
    "Number": [
      "number"
    ],
    "Options": [
      "options"
    ],
    "Including": [
      "including"
    ],
    "Free": [
      "free"
    ],
    "Without": [
      "without"
    ],
    "Best": [
      "best"
    ],
    "Digital": [
      "digital"
    ],
    "Web": [
      "web"
    ],
    "Direct": [
      "direct",
      "channels"
    ],
    "View": [
      "view"
    ],
    "CEO": [
      "CEO"
    ],
    "Management": [
      "management"
    ],
    "Team": [
      "team"
    ],
    "Before": [
      "before"
    ],
    "Part": [
      "part"
    ],
    "Idea": [
      "idea",
      "did"
    ],
    "Important": [
      "important"
    ],
    "Agency": [
      "agency"
    ],
    "Rental": [
      "rental"
    ],
    "Within": [
      "within"
    ],
    "Project": [
      "project"
    ],
    "Destinations": [
      "destinations"
    ],
    "Process": [
      "process"
    ],
    "Example": [
      "example"
    ],
    "Similar": [
      "similar"
    ]
  },
  "2013-08": {
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Social Media": [
      "social",
      "media",
      "social media",
      "network",
      "networks"
    ],
    "Data": [
      "data",
      "information"
    ],
    "Users": [
      "users",
      "trip",
      "friends"
    ],
    "Airlines": [
      "airlines",
      "airline"
    ],
    "Online": [
      "online"
    ],
    "Bookings": [
      "booking",
      "help",
      "bookings",
      "tour",
      "direct",
      "OTAs",
      "agencies",
      "book",
      "then",
      "channel",
      "going",
      "agency",
      "access",
      "agents",
      "needs",
      "available",
      "offer",
      "rates",
      "inventory",
      "rate",
      "channels",
      "focus",
      "tours",
      "operators",
      "suppliers",
      "businesses",
      "offers",
      "directly",
      "able",
      "find",
      "create",
      "go"
    ],
    "Search": [
      "search",
      "metasearch"
    ],
    "Marketing": [
      "marketing"
    ],
    "Mobile": [
      "mobile"
    ],
    "Online Travel": [
      "expedia",
      "com",
      "TripAdvisor",
      "Travelocity",
      "reviews"
    ],
    "Product": [
      "product"
    ],
    "First": [
      "first"
    ],
    "App": [
      "app"
    ],
    "SYSTEMS": [
      "platform",
      "system",
      "SYSTEMS"
    ],
    "Technology": [
      "technology"
    ],
    "World": [
      "world"
    ],
    "Around": [
      "around"
    ],
    "Consumers": [
      "consumers",
      "travelers",
      "travellers",
      "consumer"
    ],
    "Tech Companies": [
      "Google"
    ],
    "Results": [
      "results"
    ],
    "Traffic": [
      "traffic"
    ],
    "Full Story": [
      "Tnooz",
      "full",
      "story",
      "read",
      "full story",
      "Read the full"
    ],
    "Web": [
      "web"
    ],
    "Sites": [
      "sites",
      "brand",
      "website",
      "site",
      "brands",
      "websites"
    ],
    "Distribution": [
      "distribution",
      "global"
    ],
    "Experiences": [
      "experience",
      "experiences"
    ],
    "Revenue": [
      "revenue"
    ],
    "Management": [
      "management"
    ],
    "Across": [
      "across"
    ],
    "Startups": [
      "startup",
      "startups"
    ],
    "Content": [
      "content"
    ],
    "Vacation": [
      "vacation",
      "car",
      "rental"
    ],
    "Between": [
      "between"
    ],
    "Digital": [
      "digital"
    ],
    "Local": [
      "local"
    ],
    "Growth": [
      "growth",
      "significant"
    ],
    "Top": [
      "top"
    ],
    "CEO": [
      "CEO",
      "co-founder"
    ],
    "Best": [
      "best"
    ],
    "Take": [
      "take"
    ],
    "Strategy": [
      "strategy"
    ],
    "Important": [
      "important"
    ],
    "Share": [
      "share"
    ],
    "August": [
      "August",
      "week",
      "August 2013",
      "launched",
      "July"
    ],
    "Number": [
      "number"
    ],
    "Model": [
      "model"
    ],
    "Another": [
      "another"
    ],
    "American": [
      "American"
    ],
    "Yet": [
      "yet"
    ],
    "Deal": [
      "deal"
    ],
    "Made": [
      "made"
    ],
    "According": [
      "according",
      "study"
    ],
    "Products": [
      "products"
    ],
    "Program": [
      "program"
    ],
    "Including": [
      "including"
    ],
    "Based": [
      "based"
    ],
    "Does": [
      "does",
      "don't"
    ],
    "Example": [
      "example"
    ],
    "Four": [
      "four"
    ],
    "Own": [
      "own"
    ],
    "Work": [
      "work"
    ],
    "Become": [
      "become"
    ],
    "DURING": [
      "DURING"
    ],
    "Every": [
      "every"
    ],
    "Tourism": [
      "tourism"
    ],
    "News": [
      "news"
    ],
    "Day": [
      "day"
    ],
    "Free": [
      "free"
    ],
    "Part": [
      "part"
    ],
    "Used": [
      "used"
    ],
    "Right": [
      "right"
    ],
    "Without": [
      "without"
    ],
    "Quality": [
      "quality"
    ],
    "Idea": [
      "idea"
    ],
    "Already": [
      "already"
    ],
    "My": [
      "my"
    ]
  },
  "2013-09": {
    "Hotels": [
      "hotel",
      "hotels"
    ],
    "Mobile": [
      "mobile"
    ],
    "Social Media": [
      "social",
      "media",
      "social media",
      "network",
      "networks"
    ],
    "Online": [
      "online"
    ],
    "Bookings": [
      "booking",
      "help",
      "bookings",
      "access",
      "go",
      "then",
      "want",
      "provide",
      "available",
      "book",
      "find",
      "right",
      "able",
      "offer",
      "create",
      "offering",
      "looking",
      "going"
    ],
    "Data": [
      "data",
      "information"
    ],
    "Users": [
      "users"
    ],
    "Technology": [
      "technology"
    ],
    "Apps": [
      "app",
      "apps",
      "devices",
      "internet"
    ],
    "Airlines": [
      "airlines",
      "airline",
      "air"
    ],
    "Experience": [
      "experience"
    ],
    "Product": [
      "product"
    ],
    "Travelers": [
      "travelers",
      "travellers",
      "consumers",
      "guests",
      "traveler"
    ],
    "Content": [
      "content"
    ],
    "Marketing": [
      "marketing"
    ],
    "First": [
      "first"
    ],
    "Search": [
      "search"
    ],
    "Social Media #2": [
      "Facebook",
      "twitter"
    ],
    "Tech Companies": [
      "Google"
    ],
    "Around": [
      "around"
    ],
    "Reviews": [
      "reviews",
      "review"
    ],
    "Wifi": [
      "wifi",
      "airport",
      "free",
      "passengers"
    ],
    "Trip": [
      "trip",
      "planning"
    ],
    "Brands": [
      "brands",
      "brand",
      "websites",
      "website",
      "sites",
      "site"
    ],
    "Online Travel": [
      "com",
      "Expedia"
    ],
    "Revenue": [
      "revenue"
    ],
    "World": [
      "world"
    ],
    "Destination": [
      "destination"
    ],
    "Own": [
      "own"
    ],
    "Share": [
      "share"
    ],
    "Tnooz": [
      "Tnooz"
    ],
    "Products": [
      "products"
    ],
    "Group": [
      "group"
    ],
    "Systems": [
      "system",
      "platform",
      "systems"
    ],
    "Become": [
      "become"
    ],
    "Part": [
      "part"
    ],
    "Take": [
      "take"
    ],
    "Number": [
      "number"
    ],
    "Model": [
      "model"
    ],
    "September": [
      "September",
      "launched",
      "news",
      "September 2013",
      "launches"
    ],
    "Another": [
      "another"
    ],
    "Management": [
      "management"
    ],
    "Including": [
      "including"
    ],
    "Guest": [
      "guest"
    ],
    "Strategy": [
      "strategy"
    ],
    "CEO": [
      "CEO"
    ],
    "Flight": [
      "flight"
    ],
    "Team": [
      "team"
    ],
    "Between": [
      "between"
    ],
    "Digital": [
      "digital"
    ],
    "Global": [
      "global"
    ],
    "My": [
      "my"
    ],
    "Potential": [
      "potential"
    ],
    "Loyalty": [
      "loyalty",
      "engagement"
    ],
    "Before": [
      "before"
    ],
    "Hospitality": [
      "hospitality"
    ],
    "Example": [
      "example"
    ],
    "Based": [
      "based"
    ],
    "Future": [
      "future"
    ],
    "Agents": [
      "agents"
    ],
    "Across": [
      "across"
    ],
    "Best": [
      "best"
    ],
    "Already": [
      "already"
    ],
    "Tours": [
      "tour",
      "tours"
    ],
    "Today": [
      "today",
      "yet",
      "too"
    ],
    "Destinations": [
      "destinations"
    ],
    "Used": [
      "used"
    ],
    "Process": [
      "process"
    ],
    "Without": [
      "without"
    ],
    "Local": [
      "local"
    ],
    "Page": [
      "page"
    ],
    "OTAs": [
      "OTAs"
    ],
    "Web": [
      "web"
    ],
    "Recent": [
      "recent"
    ],
    "Car": [
      "car",
      "rental"
    ],
    "Growth": [
      "growth"
    ],
    "Investments & M&A": [
      "startup",
      "funding"
    ],
    "Luxury": [
      "luxury"
    ],
    "Average": [
      "average",
      "less"
    ],
    "Key": [
      "key"
    ],
    "Point": [
      "point"
    ],
    "Comes": [
      "comes"
    ],
    "Room": [
      "room"
    ],
    "Given": [
      "given"
    ],
    "Research": [
      "research"
    ],
    "Work": [
      "work"
    ],
    "Top": [
      "top"
    ],
    "Full": [
      "full"
    ],
    "Development": [
      "development"
    ],
    "Good": [
      "good"
    ],
    "Space": [
      "space"
    ],
    "Campaign": [
      "campaign"
    ],
    "Every": [
      "every"
    ]
  },
  "2013-10": {
    "Hotels": [
      "hotel",
      "hotels",
      "property"
    ],
    "Data": [
      "data",
      "information"
    ],
    "Mobile": [
      "mobile"
    ],
    "Bookings": [
      "booking",
      "bookings",
      "book"
    ],
    "Social Media": [
      "social",
      "media",
      "social media"
    ],
    "Online": [
      "online"
    ],
    "Marketing": [
      "marketing"
    ],
    "Airlines": [
      "airlines",
      "airline",
      "air"
    ],
    "Search": [
      "search"
    ],
    "Content": [
      "content"
    ],
    "Digital": [
      "digital"
    ],
    "Tech Companies": [
      "Google"
    ],
    "Technology": [
      "technology"
    ],
    "Travelers": [
      "travellers",
      "travelers",
      "consumers",
      "trip",
      "planning",
      "trips",
      "plan",
      "traveler"
    ],
    "Users": [
      "users"
    ],
    "Reviews": [
      "TripAdvisor",
      "reviews",
      "review",
      "com",
      "expedia",
      "OTAs",
      "OTA"
    ],
    "Experience": [
      "experience"
    ],
    "DISTRIBUTION": [
      "DISTRIBUTION",
      "global"
    ],
    "Report": [
      "report",
      "study",
      "research"
    ],
    "Product": [
      "product"
    ],
    "Sites": [
      "sites",
      "websites",
      "site",
      "brand",
      "website",
      "brands"
    ],
    "Social Media #2": [
      "Facebook"
    ],
    "Revenue": [
      "revenue"
    ],
    "Own": [
      "own"
    ],
    "Points": [
      "points",
      "loyalty"
    ],
    "First": [
      "first"
    ],
    "Across": [
      "across"
    ],
    "Number": [
      "number"
    ],
    "App": [
      "app",
      "internet",
      "devices"
    ],
    "Read": [
      "read"
    ],
    "Management": [
      "management"
    ],
    "Local": [
      "local"
    ],
    "Results": [
      "results"
    ],
    "Top": [
      "top"
    ],
    "Model": [
      "model"
    ],
    "Around": [
      "around"
    ],
    "World": [
      "world"
    ],
    "Then": [
      "then",
      "want",
      "help",
      "work",
      "especially",
      "go",
      "focus",
      "going",
      "likely",
      "often",
      "given",
      "able",
      "know",
      "become",
      "right",
      "pay",
      "come",
      "looking",
      "does",
      "less",
      "far",
      "back",
      "don't"
    ],
    "Take": [
      "take"
    ],
    "Strategy": [
      "strategy"
    ],
    "Made": [
      "made"
    ],
    "Best": [
      "best"
    ],
    "Activities": [
      "activities"
    ],
    "Platform": [
      "platform",
      "system",
      "tools",
      "process"
    ],
    "Growth": [
      "growth",
      "traffic",
      "spend",
      "increase"
    ],
    "Destination": [
      "destination"
    ],
    "Tnooz": [
      "tnooz"
    ],
    "Team": [
      "team"
    ],
    "Payment": [
      "payment",
      "card"
    ],
    "Used": [
      "used"
    ],
    "Example": [
      "example"
    ],
    "Day": [
      "day"
    ],
    "Flight": [
      "flight"
    ],
    "Another": [
      "another"
    ],
    "Price": [
      "price"
    ],
    "Key": [
      "key"
    ],
    "Vacation": [
      "vacation"
    ],
    "Tourism": [
      "tourism"
    ],
    "Recent": [
      "recent"
    ],
    "Said": [
      "said"
    ],
    "Share": [
      "share"
    ],
    "Today": [
      "today"
    ],
    "TripConnect": [
      "TripConnect"
    ],
    "Point": [
      "point"
    ],
    "Space": [
      "space"
    ],
    "Based": [
      "based",
      "specific"
    ],
    "Businesses": [
      "businesses"
    ],
    "Having": [
      "having"
    ],
    "Part": [
      "part"
    ],
    "Agents": [
      "agents"
    ],
    "Every": [
      "every"
    ],
    "Available": [
      "available"
    ],
    "Between": [
      "between"
    ],
    "Channels": [
      "channels",
      "direct"
    ],
    "Among": [
      "among"
    ],
    "Startup": [
      "startup"
    ],
    "Web": [
      "web"
    ],
    "Terms": [
      "terms"
    ],
    "Including": [
      "including"
    ],
    "Provide": [
      "provide"
    ],
    "Destinations": [
      "Asia"
    ],
    "Deal": [
      "deal"
    ],
    "Group": [
      "group"
    ],
    "Within": [
      "within"
    ],
    "Products": [
      "products"
    ]
  }
}


# 英文停用词列表
ENGLISH_STOP_WORDS = {
    # 人称代词
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 'your', 'yours', 
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    
    # 疑问词和指示词
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'where', 'when', 'why', 'how',
    
    # 常见动词
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'shall', 'will', 'might',
    'must', 'may', 'says', 'said', 'say', 'like', 'liked', 'want', 'wants', 'wanted',
    'get', 'gets', 'got', 'make', 'makes', 'made', 'see', 'sees', 'saw', 'look', 'looks',
    'looking', 'take', 'takes', 'took', 'come', 'comes', 'came',
    
    # 介词和连词
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 
    'off', 'over', 'under', 'again', 'further', 'than',
    
    # 时间和数量词
    'now', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'first', 'last', 'many', 'much', 'one', 'two', 'three',
    'next', 'previous', 'today', 'tomorrow', 'yesterday', 'day', 'week', 'month', 'year',
    
    # 其他常见词
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'too', 'very', 'just', 'well',
    'also', 'back', 'even', 'still', 'way', 'ways', 'thing', 'things', 'new', 'old',
    'good', 'better', 'best', 'bad', 'worse', 'worst', 'high', 'low', 'possible',
    'different', 'early', 'late', 'later', 'latest', 'hard', 'easy', 'earlier',
    
    # 缩写和常见组合
    "don't", 'cant', "can't", 'wont', "won't", "isn't", "aren't", "wasn't", "weren't",
    "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't", "shouldn't", "wouldn't",
    "couldn't", "mustn't", "mightn't", "shan't", 'let', "let's", 'lets',
}

# 过滤掉的特定高频词
FILTERED_WORDS = {
    'travel', 'hotel', 'hotels', 'company', 'companies', 'business', 'million', 'billion',
    'market', 'markets', 'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days',
    'time', 'times', 'report', 'reported', 'according', 'says', 'said', 'say', 'told',
    'announced', 'launched', 'based', 'include', 'includes', 'including', 'included',
    'percent', 'percentage', 'number', 'numbers', 'group', 'groups', 'service', 'services',
    'use', 'used', 'using', 'provide', 'provides', 'provided', 'providing', 'make', 'makes',
    'made', 'making', 'set', 'sets', 'setting', 'need', 'needs', 'needed', 'needing',
    'work', 'works', 'working', 'worked', 'call', 'calls', 'called', 'calling',
    'find', 'finds', 'finding', 'found', 'show', 'shows', 'showed', 'shown', 'showing',
    'think', 'thinks', 'thinking', 'thought', 'way', 'ways', 'thing', 'things',
    'people', 'person', 'world', 'global', 'international', 'domestic', 'local',
    'industry', 'industries', 'sector', 'sectors', 'customer', 'customers',
    'data', 'information', 'technology', 'technologies', 'platform', 'platforms',
    'solution', 'solutions', 'system', 'systems', 'product', 'products',
    'place', 'places', 'area', 'areas', 'region', 'regions', 'country', 'countries',
    'city', 'cities', 'state', 'states', 'part', 'parts', 'end', 'ends', 'start', 'starts',
    'level', 'levels', 'rate', 'rates', 'value', 'values', 'price', 'prices',
    'cost', 'costs', 'revenue', 'revenues', 'sale', 'sales', 'growth', 'increase',
    'decrease', 'change', 'changes', 'changed', 'changing', 'development', 'developments',
    'plan', 'plans', 'planned', 'planning', 'strategy', 'strategies', 'strategic',
    'operation', 'operations', 'operating', 'operated', 'management', 'managing',
    'managed', 'manager', 'managers', 'executive', 'executives', 'director', 'directors',
    'leader', 'leaders', 'leadership', 'team', 'teams', 'staff', 'employee', 'employees',
    'partner', 'partners', 'partnership', 'partnerships', 'client', 'clients',
    'user', 'users', 'consumer', 'consumers', 'visitor', 'visitors', 'guest', 'guests',
    'passenger', 'passengers', 'traveler', 'travelers', 'tourist', 'tourists',
    'booking', 'bookings', 'booked', 'reservation', 'reservations', 'reserved',
    'flight', 'flights', 'airline', 'airlines', 'airport', 'airports',
    'destination', 'destinations', 'location', 'locations', 'site', 'sites',
    'property', 'properties', 'room', 'rooms', 'accommodation', 'accommodations',
    'tour', 'tours', 'trip', 'trips', 'experience', 'experiences', 'experienced',
    'offer', 'offers', 'offered', 'offering', 'deal', 'deals', 'option', 'options',
    'feature', 'features', 'featured', 'featuring', 'support', 'supports', 'supported',
    'supporting', 'help', 'helps', 'helped', 'helping', 'create', 'creates', 'created',
    'creating', 'build', 'builds', 'building', 'built', 'develop', 'develops',
    'developed', 'developing', 'launch', 'launches', 'launched', 'launching',
    'implement', 'implements', 'implemented', 'implementing', 'introduce', 'introduces',
    'introduced', 'introducing', 'bring', 'brings', 'bringing', 'brought',
    # 添加新的过滤词
    'phocuswire', 'phocuswright', 'subscribe', 'subscribed', 'subscription',
    'click', 'clicks', 'read', 'reads', 'reading', 'view', 'views', 'viewing',
    'follow', 'follows', 'following', 'followed', 'join', 'joins', 'joining', 'joined',
    'sign', 'signs', 'signing', 'signed', 'register', 'registers', 'registering', 'registered',
    'newsletter', 'newsletters', 'email', 'emails', 'contact', 'contacts', 'contacting',
    'news', 'article', 'articles', 'story', 'stories', 'post', 'posts', 'posting',
    'content', 'contents', 'page', 'pages', 'site', 'sites', 'website', 'websites'
}

# 添加双词短语的过滤集合
IMPORTANT_BIGRAMS = {
    'artificial intelligence', 'machine learning', 'deep learning',
    'travel industry', 'business travel', 'online travel',
    'travel management', 'digital transformation', 'customer experience',
    'mobile app', 'real time', 'artificial intelligence',
    'revenue management', 'data analytics', 'business model',
    'travel technology', 'booking platform', 'travel platform',
    'travel agency', 'travel agencies', 'corporate travel',
    'travel demand', 'travel market', 'travel sector',
    'travel tech', 'travel trends', 'travel distribution',
    'travel startup', 'travel startups', 'travel ecosystem',
    'travel payments', 'travel recovery', 'travel restrictions',
    'virtual reality', 'augmented reality', 'blockchain technology',
    'big data', 'cloud computing', 'internet things',
    'user experience', 'supply chain', 'market share',
}

# 添加要过滤的双词短语
FILTERED_BIGRAMS = {
    'last year', 'next year', 'last month', 'next month',
    'last week', 'next week', 'per cent', 'press release',
    'chief executive', 'vice president', 'executive officer',
    'read more', 'find out', 'learn more', 'click here',
    'full story', 'full article', 'more information',
}

class WordObj:
    def __init__(self, text, color=None):
        self.text = text
        # 生成深色以确保在白色背景上可见
        if color is None:
            # 确保RGB值不会太高（避免太浅的颜色）
            r = randint(0, 180)
            g = randint(0, 180)
            b = randint(0, 180)
            # 确保至少有一个通道的颜色足够深
            min_darkness = 50
            if builtins.max(r, g, b) > min_darkness:
                darkest_channel = randint(0, 2)
                if darkest_channel == 0:
                    r = randint(0, min_darkness)
                elif darkest_channel == 1:
                    g = randint(0, min_darkness)
                else:
                    b = randint(0, min_darkness)
            self.color = (r, g, b)
        else:
            self.color = color
        self.font = None
        self.surface = None
        self.size = 1.0
        self.update_surface()
        
    def update_surface(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.Font(None, int(32 * self.size))
        self.surface = self.font.render(self.text, True, self.color)
        rect = self.surface.get_rect()
        self.width = rect.width / 20.0  # Scale down for Box2D
        self.height = rect.height / 20.0
        self.aspect_ratio = self.width / self.height

class WordSwarm:
    def __init__(self, data_dir="output", output_dir="animation_results"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.articles = []
        self.word_frequencies = {}
        self.dates = []
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(output_dir, "frames")).mkdir(parents=True, exist_ok=True)
        
        # 初始化PyGame（使用离屏渲染）
        pygame.init()
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # 使用虚拟显示
        self.screen = pygame.Surface((1920, 1080))
        
        # 创建Box2D世界 - 调整重力为向中心
        self.world = b2World(gravity=(0, 0))
        
        # 动画相关参数 - 调整以获得更好的效果
        self.frequency = 0.5  # 增加频率使运动更快
        self.damping = 1.0   # 减小阻尼使运动更流畅
        self.max_size = 3.0  # 调整最大尺寸
        self.min_size = 0.5  # 调整最小尺寸
        self.transition_frames = 144  # 设置过渡帧数以实现5分钟视频（144帧/过渡 * 50时间点 ÷ 24fps ≈ 300秒）
        
        # 中心点坐标（屏幕中心）
        self.center_x = 0
        self.center_y = 0
        
        # 存储单词对象和它们的目标状态
        self.word_objects = []
        self.bodies = []
        self.joints = []
        self.center_body = None
        self.target_sizes = {}  # 存储目标大小
        
        # 设置中心引力场
        self.setup_center_gravity()
    def apply_repulsion_between_words(self, min_distance=1.5, strength=2.0):
        """让所有词之间互相排斥，防止集中在中心堆叠"""
        for i, body_a in enumerate(self.bodies):
            for j, body_b in enumerate(self.bodies):
                if i >= j:
                    continue
                delta = body_b.position - body_a.position
                distance = delta.length
                if distance < min_distance and distance > 0.01:
                    # 标准化方向
                    delta.Normalize()
                    # 距离越近，力越强
                    force = strength * (min_distance - distance)
                    body_a.ApplyForce(-delta * force, body_a.worldCenter, True)
                    body_b.ApplyForce(delta * force, body_b.worldCenter, True)

    def setup_center_gravity(self):
        """设置中心引力场"""
        # 创建中心锚点
        self.center_body = self.world.CreateStaticBody(
            position=(self.center_x, self.center_y)
        )

    def load_data(self):
        """从JSON文件加载文章数据"""
        json_files = glob.glob(os.path.join(self.data_dir, "phocuswire_page_*.json"))
        all_articles = []
        
        print(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in tqdm(json_files, desc="加载文章数据"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    all_articles.extend(articles)
            except Exception as e:
                print(f"读取文件 {json_file} 时出错: {e}")
        
        print(f"总共加载了 {len(all_articles)} 篇文章")
        self.articles = all_articles
        return all_articles

    def process_articles(self):
        """处理文章数据，提取关键词频率"""
        word_freq_by_date = {}
        dates = set()
        
        for article in tqdm(self.articles, desc="处理文章"):
            try:
                date_str = article.get('date')
                if not date_str:
                    continue
                    
                date_obj = self.parse_date(date_str)
                if not date_obj:
                    continue
                
                # 将日期转换为年月格式
                year_month = date_obj.strftime("%Y-%m")
                dates.add(year_month)
                
                # 预处理文章内容
                content = article.get('content', '')
                words = self.preprocess_text(content)
                
                # 更新词频
                if year_month not in word_freq_by_date:
                    word_freq_by_date[year_month] = {}
                
                for word in words:
                    word_freq_by_date[year_month][word] = word_freq_by_date[year_month].get(word, 0) + 1
                    
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        self.word_frequencies = word_freq_by_date
        self.dates = sorted(list(dates))
        
    def interpolate_sizes(self, current_freqs, next_freqs, progress):
        """在两个时间点之间平滑插值词频"""
        sizes = {}
        max_current = builtins.max(current_freqs.values()) if current_freqs else 1
        max_next = builtins.max(next_freqs.values()) if next_freqs else 1
        
        for word in set(current_freqs.keys()) | set(next_freqs.keys()):
            current_freq = current_freqs.get(word, 0)
            next_freq = next_freqs.get(word, 0)
            
            # 使用平滑插值
            current_size = self.min_size + (self.max_size - self.min_size) * (current_freq / max_current)
            next_size = self.min_size + (self.max_size - self.min_size) * (next_freq / max_next)
            
            # 使用三次方插值使过渡更平滑
            t = progress
            t = t * t * (3 - 2 * t)  # 平滑插值函数
            sizes[word] = current_size * (1 - t) + next_size * t
            
        return sizes

    def create_animation(self, custom_words=None):
        """创建基于物理引擎的词云动画，使用自定义关键词列表"""
        if not self.word_frequencies or not self.dates:
            print("请先运行 process_articles() 方法")
            return
        
        all_words = custom_words if custom_words is not None else CUSTOM_WORDS
        all_words = list(dict.fromkeys(all_words))  # 去重，保持顺序
        
        # 创建单词对象和物理体（与原逻辑一致，但只针对all_words）
        self.word_objects = []
        self.bodies = []
        self.joints = []
        positions = []
        for i, word in enumerate(all_words):
            word_obj = WordObj(word)
            max_r = 30.0
            max_attempts = 50
            for attempt in range(max_attempts):
                angle = uniform(0, 2 * math.pi)
                radius = uniform(1.0, max_r)
                init_x = radius * math.cos(angle) + uniform(-0.5, 0.5)
                init_y = radius * math.sin(angle) + uniform(-0.5, 0.5)
                min_dist = 2.5
                too_close = False
                for px, py in positions:
                    dist = math.sqrt((init_x - px) ** 2 + (init_y - py) ** 2)
                    if dist < min_dist:
                        too_close = True
                        break
                if not too_close:
                    break
            positions.append((init_x, init_y))
            self.word_objects.append(word_obj)
            body = self.world.CreateDynamicBody(
                position=(init_x, init_y),
                linearDamping=0.8,
                angularDamping=0.9,
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(word_obj.width/2, word_obj.height/2)),
                    density=1.0,
                    friction=0.3,
                    restitution=0.1
                )
            )
            initial_linear_velocity = b2Vec2(uniform(-1.5, 1.5), uniform(-1.5, 1.5))
            body.linearVelocity = initial_linear_velocity
            self.bodies.append(body)
            self.apply_repulsion_between_words()
            dist_to_center = math.sqrt(init_x * init_x + init_y * init_y)
            joint = self.world.CreateDistanceJoint(
                bodyA=self.center_body,
                bodyB=body,
                anchorA=self.center_body.position,
                anchorB=body.position,
                frequencyHz=self.frequency,
                dampingRatio=self.damping,
                length=dist_to_center * 1
            )
            self.joints.append(joint)
        # 动画循环（只做整体动画，不分时间段）
        frame_count = 0
        total_frames = 300  # 固定帧数
        print("正在生成动画帧...")
        for frame in tqdm(range(total_frames)):
            self.screen.fill((255, 255, 255))
            self.world.Step(1.0/60.0, 8, 3)
            for i, word_obj in enumerate(self.word_objects):
                # 统计所有时间的最大频率
                max_freq = 1
                freq = 0
                for date in self.dates:
                    freq = builtins.max(freq, self.word_frequencies.get(date, {}).get(word_obj.text, 0))
                    max_freq = builtins.max(max_freq, freq)
                # 取最大频率决定大小
                target_size = self.min_size + (self.max_size - self.min_size) * (freq / max_freq)
                word_obj.size = target_size
                word_obj.update_surface()
                body = self.bodies[i]
                fixture = body.fixtures[0]
                body.DestroyFixture(fixture)
                body.CreateFixture(
                    shape=b2PolygonShape(box=(word_obj.width * target_size / 2, 
                                            word_obj.height * target_size / 2)),
                    density=1.0,
                    friction=0.3,
                    restitution=0.1
                )
                pos = body.position
                screen_pos = (int(pos.x * 20 + self.screen.get_width()/2),
                            int(-pos.y * 20 + self.screen.get_height()/2))
                text_rect = word_obj.surface.get_rect()
                screen_pos = (screen_pos[0] - text_rect.width//2,
                            screen_pos[1] - text_rect.height//2)
                self.screen.blit(word_obj.surface, screen_pos)
            # 绘制关键词说明
            font = pygame.font.Font(None, 48)
            date_surface = font.render("Custom Word Swarm", True, (50, 50, 50))
            date_rect = date_surface.get_rect()
            date_rect.topright = (self.screen.get_width() - 50, 50)
            self.screen.blit(date_surface, date_rect)
            pygame.image.save(self.screen, 
                            os.path.join(self.output_dir, "frames", f"frame_{frame_count:04d}.png"))
            frame_count += 1
        output_path = os.path.join(self.output_dir, 'word_swarm_custom.mp4')
        cmd = (f"ffmpeg -y -framerate 30 -i {os.path.join(self.output_dir, 'frames', 'frame_%04d.png')} "
               f"-vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' "
               f"-c:v libx264 -pix_fmt yuv420p -crf 18 {output_path}")
        os.system(cmd)
        print(f"动画已保存至: {output_path}")
        pygame.quit()
    
    def parse_date(self, date_str):
        """解析日期字符串为日期对象"""
        try:
            date_formats = [
                "%B %d, %Y",
                "%d %B %Y",
                "%B %Y",
                "%Y-%m-%d",
            ]
            
            for date_format in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), date_format)
                except ValueError:
                    continue
                    
            return None
        except:
            return None
    
    def preprocess_text(self, text):
        """预处理文本，支持单词和双词短语"""
        if not text:
            return []
            
        # 移除非字母字符，但保留空格
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        
        # 分词
        words = [word.strip() for word in text.split() if word.strip()]
        
        # 提取单词和双词短语
        processed_terms = []
        
        # 处理双词短语
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            # 如果是重要的双词短语，添加到结果中
            if bigram in IMPORTANT_BIGRAMS and bigram not in FILTERED_BIGRAMS:
                processed_terms.append(bigram)
        
        # 处理单个词
        # 只处理那些不是双词短语一部分的单词
        for i, word in enumerate(words):
            # 检查这个词是否是任何重要双词短语的一部分
            is_part_of_bigram = False
            if i < len(words) - 1:
                current_bigram = f"{word} {words[i+1]}"
                if current_bigram in IMPORTANT_BIGRAMS:
                    is_part_of_bigram = True
            if i > 0:
                previous_bigram = f"{words[i-1]} {word}"
                if previous_bigram in IMPORTANT_BIGRAMS:
                    is_part_of_bigram = True
            
            # 如果不是双词短语的一部分，且符合其他条件，则添加这个单词
            if not is_part_of_bigram and word not in ENGLISH_STOP_WORDS and word not in FILTERED_WORDS and len(word) > 2:
                processed_terms.append(word)
        
        return processed_terms

if __name__ == "__main__":
    # 创建WordSwarm实例
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animation_results")
    
    swarm = WordSwarm(data_dir=data_dir, output_dir=output_dir)
    
    # 加载和处理数据
    swarm.load_data()
    swarm.process_articles()
    
    # 创建动画
    swarm.create_animation(custom_words=CUSTOM_WORDS) 