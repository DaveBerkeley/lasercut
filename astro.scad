
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
    width = r_outer / 30;
    pointer = r_outer / 10;
    length = (r_outer / 10) * ext;
    z = thick;
    translate([ x, y, 0 ])
    {
        rotate(a=angle)
        {
            union()
            {
                linear_extrude(height=z)
                    polygon(points=[ 
                        [0,0], 
                        [-pointer, width/2], [-pointer, width/2], 
                        [-pointer, -width/2], [-pointer, -width/2],
                        [0, 0],
                    ]);
                translate([-(pointer+length), -width/2, 0])
                    cube([length, width, z]);
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
        add_star(star[1], star[2], name, -15, 0.5);
    }
    if (name == "Arcturus") 
    {
        add_star(star[1], star[2], name, 45, 0);
    }
    if (name == "Vega") 
    {
        add_star(star[1], star[2], name, -5, 1);
    }
    if (name == "Capella") 
    {
        add_star(star[1], star[2], name, 10, 1);
    }
    if (name == "Rigel") 
    {
        // no use as it lies within the ecliptic ring
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Procyon") 
    {
        add_star(star[1], star[2], name, 150, 0);
    }
    if (name == "Betelgeuse") 
    {
        add_star(star[1], star[2], name, 180, 0.6);
    }
    if (name == "Altair") 
    {
        // no use as it lies within the ecliptic ring
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Aldebaran") 
    {
        add_star(star[1], star[2], name, 200, 1);
    }
    if (name == "Spica") 
    {
        add_star(star[1], star[2], name, 70, 1);
    }
    if (name == "Pollux") 
    {
        // not sure yet where to put this
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Deneb") 
    {
        add_star(star[1], star[2], name, -35, 1.5);
    }
    if (name == "Regulus") 
    {
        add_star(star[1], star[2], name, 115, 0);
    }
    if (name == "Castor") 
    {
        // not sure yet where to put this
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Bellatrix") 
    {
        add_star(star[1], star[2], name, 190, 0);
    }
    if (name == "Elnath") 
    {
        // not sure yet where to put this
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Alnilam") 
    {
        // too close to ecliptic ring
        //add_star(star[1], star[2], name, 190, 0);
    }
    if (name == "Alioth") 
    {
        // right on the bar
        //add_star(star[1], star[2], name, 0, 1);
    }
    if (name == "Dubhe") 
    {
        // not sure about this one ..
        add_star(star[1], star[2], name, 0, 0);
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
      //  dr = r_solar_outer - r_solar_bevel; 
      //  // hypotenuse of bevel
      //  length = sqrt((z_hi*z_hi) + (dr*dr));
      //  bevel_angle = asin(z_hi / length);
      //  w = r_outer / 80;
      //  rotate(a=angle)
      //      translate([ r_solar_outer, width/2, 0])
      //          rotate(a=[0, -90, 0])
      //              rotate(a=[45, 0, 0])
      //                  translate([ 0, 0, z_lo - (w/2)])
      //                      cube([length, w, w]);
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
