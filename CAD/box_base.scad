
module body() {
    color("Red") cube([100,90,44.22]); 
}

module innerFrame() {
    color("Red") cube([80,70,60]); 
}

module smallFrame() {
    color("Red") cube([10,20,60]);     
}

module bushing() {
    cylinder (h = 23.31, r=12.5, center = true, $fn=100);    
}

module box() {
    color("grey") cube([90.33,120,160.4]); 
}
module completeBox() {
    union(){
        box();
        translate([30,60,-11.65]) bushing();
    }
}
module zip() {
    color("black") cube([2,60,160.4]);    
}


module boxes() {
     union(){         
         mirror([1,0,0]) translate([-90.33,0,0]) completeBox();
         translate([90.33,30,0]) zip();
         mirror([1,0,0]) translate([-182.66,0,0]) completeBox();
         translate([182.66,30,0]) zip();
         translate([184.66,0,0]) completeBox();         
     }
}


module base(){
    difference() {
    body();
    translate([10,10,-5]) innerFrame();
    translate([45,-5,10]) smallFrame();
    }    
}


//translate([15,9,0])
base();

//translate([169.99,9,0])
//base();

//translate([0,0,44.22])
//translate([0,0,50])
//boxes();

