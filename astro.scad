
include <stars.scad>;

thick = 6.0;
z_lo = thick * 0.3;
z_hi = thick * 0.7;

// imported from stars.scad
// rad_outer

r_width = rad_outer / 18.0;
r_outer = rad_outer;
r_inner = r_outer - r_width;

r_solar_outer = 140.0; // TODO

r_solar_width = 2.0 * r_width;
r_solar_inner = r_solar_outer - r_solar_width;
r_solar_bevel = r_solar_outer - r_width;

r_inner_disk = rad_outer / 10;
r_hole = 2.5;

// offset to centre of Ecliptic
x_solar = 20.0; // TODO

// structure holding ecliptic to outer
band = 10.0;

min_angle = 3; // todo 1;

module add_star (x, y, name, angle, ext)
{
    r = 3;
    w = r_outer / 20;
    h = w * 1.5;
    z = thick;
    translate([ x, y, 0 ])
    {
        rotate(a=angle)
        {
            union()
            {
                //cylinder(thick * 2.0, r1=r, r2=0, $fa=min_angle);
                linear_extrude(height=z)
                    polygon(points=[ 
                        [0,0], 
                        [-w, h/6], [-w, h/2], 
                        [-2*w*ext, h/2], 
                        [-2*w*ext, -h/2],
                        [-w, -h/2], [-w, -h/6],
                        [0, 0],
                    ]);
            }
        }
    }
}

// Add the stars
for (star = stars)
{
    name = star[0];
    if (name == "Sirius") 
    {
        add_star(star[1], star[2], name, -15, 1.5);
    }
    if (name == "Arcturus") 
    {
        add_star(star[1], star[2], name, 45, 1);
    }
    if (name == "Vega") 
    {
        add_star(star[1], star[2], name, -5, 2);
    }
    if (name == "Capella") 
    {
        add_star(star[1], star[2], name, 10, 2);
    }
    if (name == "Rigel") 
    {
        // no use as it lies within the ecliptic ring
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Procyon") 
    {
        add_star(star[1], star[2], name, 150, 1);
    }
    if (name == "Betelgeuse") 
    {
        add_star(star[1], star[2], name, 180, 1.5);
    }
}

// Ecliptic
translate([ x_solar, 0, 0])
{
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
    
      // graduated scale on bevel
      //for (angle = [ 0 : 5 : 360 ])
      //{
      //  width = 1.0;
      //  r = 0.2;
      //  rotate(a=angle)
      //      translate([ r_solar_outer, width/2, 0])
      //          rotate([ 0, -60, 0 ])
      //              cylinder(1, r1=r, r2=r, $fa=min_angle);
      //}
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
