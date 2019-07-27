
thick = 0.60;
z_lo = thick * 0.3;
z_hi = thick * 0.7;

r_outer = 18.00;
r_inner = 17.00;

r_solar_outer = 14.00;
r_solar_inner = 12.00;
r_solar_bevel = 13.00;

r_inner_disk = 2.00;
r_hole = 0.50;

x_solar = 3.00;

band = 1.00;

min_angle = 1; // todo 1;

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
