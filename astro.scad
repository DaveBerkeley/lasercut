
include <stars.scad>;

thick = 0.60;
z_lo = thick * 0.3;
z_hi = thick * 0.7;

// imported from stars.scad
// rad_outer

r_width = rad_outer / 18.0;
r_outer = rad_outer;
r_inner = r_outer - r_width;

r_solar_outer = 14.00; // TODO

r_solar_width = 2.0 * r_width;
r_solar_inner = r_solar_outer - r_solar_width;
r_solar_bevel = r_solar_outer - r_width;

r_inner_disk = rad_outer / 10;
r_hole = 0.50;

// offset to centre of Ecliptic
x_solar = 2.00; // TODO

// structure holding ecliptic to outer
band = 1.00;

min_angle = 1; // todo 1;

module add_star (x, y, name)
{
    translate([ x, y, 0 ])
        cylinder(thick+1, r1=1, r2=1, $fa=min_angle);
}

// Add the stars
for (star = stars)
    add_star(star[1], star[2], star[0]);

// Ecliptic
translate([ x_solar, 0, 0])
    difference()
    {
        union()
        {
            translate([ 0, 0, z_lo])
                cylinder(z_hi, r1=r_solar_outer, r2=r_solar_bevel, $fa=min_angle);
            cylinder(z_lo, r1=r_solar_outer, r2=r_solar_outer, $fa=min_angle);
        }
        cylinder(thick, r1=r_solar_inner, r2=r_solar_inner, $fa=min_angle);
    }

// Outer disk
difference()
{
    cylinder(thick, r1=r_outer, r2=r_outer, $fa=min_angle);
    
    // remove the inner disk
    cylinder(thick, r1=r_inner, r2=r_inner, $fa=min_angle);
    
    // remove the top 90 degree arc
    rotate(a=-45)
        cube([ r_outer, r_outer, thick]);
}

// Horizontal Bar and Centre
difference()
{
    union()
    {
        translate([-band, -r_inner, 0])
            cube([band, r_inner*2, thick]);
        cylinder(thick, r1=r_inner_disk, r2=r_inner_disk, $fa=min_angle);
    }
    cylinder(thick, r1=r_hole, r2=r_hole, $fa=min_angle);
}

//  FIN