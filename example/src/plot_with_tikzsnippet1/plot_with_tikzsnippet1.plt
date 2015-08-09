#! /usr/bin/gnuplot
#################
#
#
#################

set term tikz scale 1, 1

set yrange [0:]
set xrange [0:1200]
set xlabel 'Time (min)'
set ylabel 'Weight (g)'

set arrow 1 from 560,0.1 to 560,0.5 nohead lt 10 lc -1
set arrow 2 from 490,0.55 to 490,0.3 lt -1
set label "Cracks" at 410,0.57


plot \
'data.dat' u ($1/60):2 every 30 title "" w line
