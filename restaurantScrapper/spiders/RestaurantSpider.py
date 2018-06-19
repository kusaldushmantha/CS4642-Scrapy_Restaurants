#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 12:19:29 2018

@author: kusal
"""

import scrapy
import re

class RestaurantScraper(scrapy.Spider):
    name = "restaurants"

    def start_requests(self):
        urls = [
            'http://www.tasty.lk/restaurants?sort=p&order=d&page=1'
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for restaurant in response.css(
                'div.media-body h4.media-heading a::attr(href)').extract():
            yield scrapy.Request(restaurant, self.parse_restaurant)
        
        next_page = response.css('div#main ul.pagination li:last-child a::attr(href)').extract_first()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)
    
    def parse_restaurant(self, response):
        
        restaurant_name = response.css('div#wrap div#main h1#rest-title::text').extract_first()
        restaurant_name = re.sub('\s+', '', restaurant_name)
        address = response.css('div#wrap div#main span.address span::text').extract_first()
        address = address.strip()                       
        cuisine_list = response.css('div#wrap div#main p.cuisine a span::text').extract()
        cuisine_list = [x.strip(' ') for x in cuisine_list]
        cuisine_list = list(filter(None, cuisine_list))
        cuisine = " ".join(str(x) for x in cuisine_list)
        open_hours = response.css('div#wrap div#main p a#openHours::text').extract_first()
        if(open_hours):                          
            open_at = open_hours[7:15].strip()
            open_at = open_at.replace(" ", "")
            close_at = open_hours[18:26].strip()
            close_at = close_at.replace(" ","")
        else:
            open_at = None
            close_at = None

        phone_list = response.css('div#wrap div#main ul.contact-info li.phone a::text').extract()
        phone_list = [x.strip(' ') for x in phone_list]
        phone_list = list(filter(None, phone_list))
        phone = " ".join(str(x) for x in phone_list)                      
        price = response.css('div#wrap div#main p.price-range span::text').extract_first()
        description = response.css('div#wrap div#main div.panel div.description-info p::text').extract_first()
        facility_list = response.css('div#wrap div#main ul.main-facilities li::text').extract()
        facility = ""
        if(facility_list):                             
            for f in facility_list:
                facility = facility + ","+f.strip()
        rating_from_five = response.css('div#wrap div#main div.reviewScore span.rating-total::text').extract_first()
                                        
        yield {
            'Restaurant_name': restaurant_name,
            'Address': address,
            'Cuisine' : cuisine,
            'open_at' : open_at,
            'close_at' : close_at,
            'Call': phone,
            'Average_price': price,
            'description' : description,
            'facilities' : facility,
            'rating': rating_from_five
        }
        