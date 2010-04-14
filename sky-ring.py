#!/usr/bin/env python
# -*- coding: utf-8 -*-

# simulate a 6-month long photographic exposure of the Sun's path through the sky from a position on Earth
# inspiration: http://helpmyphysics.co.uk/wordpress/?p=276
# by way of: http://www.reddit.com/r/SomebodyMakeThis/comments/bqf2x/a_tool_to_create_sky_ring_graphs_based_on_data/

# this uses real Sun data by way of the (excellent) ephem...
# but, we tweak the track to try and match our inspirational picture...
# also, we are lacking weather data (i.e. solar magnitude due to clouds,etc.), so we
# fake it. just follow the FIXME's

import datetime
import ephem # to install, run `easy_install pyephem`
import cairo
from math import pi,radians,sin,cos,sqrt
import random # FIXME: just for naughty data-faking

filename = 'sky-ring'
height = 500.0
width = 600.0

horizon = 0

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
cr = cairo.Context(surface)
# draw background
cr.set_source_rgba(0,0,0,1)
cr.rectangle(0, 0, width, height)
cr.fill()
cr.stroke()

#o = ephem.Observer()
# Los Angeles, Calif. 34°3'N, 118°15'W
#o.lat, o.long, o.date = '34:3', '-118:15', datetime.utcnow()
# TODO: make this a parameter, or something
o = ephem.city('New York')
sun = ephem.Sun()

step = datetime.timedelta(minutes=1)
now = datetime.datetime.now()
year = now.year

when = datetime.datetime(now.year, 6, 21, 0, 0, 0)
o.date = when
sunrise = when

# for each day in the year
while when.year == year:
	# we have sunrise, now calculate sunset
	o.date = when
	s = o.next_setting(sun).tuple()
	sunset = datetime.datetime(s[0],s[1],s[2],s[3],s[4],int(s[5]))
	print('sunrise=%s sunset=%s' % (sunrise,sunset))

	# calculate today's clouds
	# TODO:

	# FIXME: fake overcast days
	if random.random() > 0.8:
		when += datetime.timedelta(days=1)
		o.date = when
	else:
		# FIXME: fake clouds
		cloudnext = when + (step * (random.randint(0,300)))
		cloudlen = random.randint(1,100)
		while when < sunset:
			if when == cloudnext:
				when += (step * cloudlen)
				cloudnext = when + (step * (random.randint(0,180)))
				cloudlen = 60 + random.randint(1,60)
			o.date = when
			sun = ephem.Sun(o)
			# FIXME: assume northern hemisphere looking dead south
			# translate sun position
			x = width - (float(sun.az) / (1.5*pi) * width) # FIXME: 2*pi
			x += width / 4 # FIXME: offset
			y0 = (float(sun.alt) / (pi/2))
			# FIXME: exagerrate y value for style :/
			y2 = -10 if y0 < 0 else y0**2*1.5
			y = (height - horizon) - (y2 * (height - horizon))
			"""
			print('date=%s az=%f alt=%f x=%f y=%f' % (o.date,float(sun.az),float(sun.alt),x,y))
			print(' ra=%f dec=%f mag=%s size=%f radius=%s earth_distance=%f az=%s(%f) alt=%s(%f)' % \
				(sun.ra, sun.dec, sun.mag, sun.size, sun.radius, sun.earth_distance, sun.az, float(sun.az), sun.alt, float(sun.alt)))
			"""
			# FIXME: set intensity of sun based on weather and position
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

# draw horizon

# save
surface.write_to_png(filename + '.jpg')
surface.finish()

print('done.')

