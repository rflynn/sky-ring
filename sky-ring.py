#!/usr/bin/env python
# -*- coding: utf-8 -*-

# simulate a 6-month long photographic exposure of the Sun's path through the sky from a position on Earth
# inspiration: http://helpmyphysics.co.uk/wordpress/?p=276
# by way of: http://www.reddit.com/r/SomebodyMakeThis/comments/bqf2x/a_tool_to_create_sky_ring_graphs_based_on_data/

# this uses real Sun data by way of the (excellent) ephem...
# but, we tweak the track to try and match our inspirational picture...
# also, we are lacking weather data (i.e. solar magnitude due to clouds,etc.), so we
# fake it. just follow the FIXME's

# http://www.reddit.com/r/pics/comments/bqa9y/the_path_of_the_sun_through_the_sky_over_the_last/c0o162g
# edit: looks like Bellshill, Scotland. The 56th parallel, so that makes sense.

# Model/Assumptions:
#  - left is due East, right is due West, horizon is 0° geometric, top is 90° geometric (i.e. straight up)
#  - center of image at the horizon is due South

# TODO's
#  - size of sun is arbitrary, figure out how to use ephem's sun.size (and maybe sun.magnitude)
#  - breaks in the sunlight (clouds) are psuedo-random to simulate real climate data. find some real climate data!

import datetime, sys, random, re
from math import pi,radians,sin,cos,sqrt
import ephem, cairo

height = 500.0
width = 600.0

horizon = height / 5

if len(sys.argv) != 2:
	print('Usage: %s location' % (sys.argv[0]))
	print('  Location can be a city name ("New York") or a latitude,longitude pair (0:0,0:0)')
	sys.exit()

loc = sys.argv[1]
print('Using location (%s)' % loc)
filename = 'sky-ring-%s.jpg' % re.sub('\W','-',loc)
print('Filename %s' % filename)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
cr = cairo.Context(surface)
# black background
cr.set_source_rgba(0,0,0,1)
cr.rectangle(0, 0, width, height)
cr.fill()
cr.stroke()

# create observer 'o' from parameter loc
o = None
if re.match('\d', loc): # lat/long
	o = ephem.Observer()
	o.lat, o.long = loc.split(',')
else:
	o = ephem.city(loc)

sun = ephem.Sun()

step = datetime.timedelta(minutes=1)
now = datetime.datetime.now()
year = now.year

# start at the summer solstice
when = datetime.datetime(now.year, 6, 21, 0, 0, 0)
o.date = when
sunrise = when

while when.month < 12 or when.day <= 21: # ...through the winter solstice
	# we have sunrise, now calculate sunset
	o.date = when
	s = o.next_setting(sun).tuple()
	sunset = datetime.datetime(s[0],s[1],s[2],s[3],s[4],int(s[5]))
	print('sunrise=%s sunset=%s' % (sunrise,sunset)) # show progress
	# FIXME: fake overcast days
	if random.random() > 0.8:
		when += datetime.timedelta(days=1)
		o.date = when
	else:
		# FIXME: fake clouds
		cloudnext = when + (step * (random.randint(0,200)))
		cloudlen = random.randint(1,100)
		while when < sunset:
			if when == cloudnext:
				when += (step * cloudlen)
				cloudnext = when + (step * (random.randint(0,180)))
				cloudlen = 60 + random.randint(1,60)
			o.date = when
			sun = ephem.Sun(o)
			# translate sun position
			x = width - (float(sun.az) / (2*pi) * width)
			# horizon = 0°, top = 90° (pi/2 radians)
			y0 = (float(sun.alt) / (pi/2))
			y = (height - horizon) - (y0 * (height - horizon))
			"""
			print('date=%s az=%f alt=%f x=%f y=%f mag=%s size=%s' % \
				(o.date, float(sun.az), float(sun.alt), x, y, sun.mag, sun.size))
			"""
			# TODO: set intensity of sun based on weather and position
			# c2f6eb
			# FIXME: force lower intensity on the edges
			cr.set_source_rgba(0.76, 0.964, 0.921, 0.3+(random.random()*0.2)-((abs(width/2-x))/width))
			# draw
			cr.arc(x, y, 2.0-((abs(width/2-x))/width), 0, 2 * pi) # FIXME: tweak sun size, middle=biggest
			cr.fill()
			# loop
			when += step
	# calculate next sunrise
	r = o.next_rising(sun).tuple()
	sunrise = datetime.datetime(r[0],r[1],r[2],r[3],r[4],int(r[5]))
	when = sunrise
cr.stroke()

# TODO: draw horizon/foreground

# save
surface.write_to_png(filename)
surface.finish()

print('%s done.' % filename)

