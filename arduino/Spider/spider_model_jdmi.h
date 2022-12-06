#pragma once

#include "spider_model.h"

class SpiderJDMI : public SpiderModel
{
    public:
        SpiderJDMI()
            : SpiderModel(
                    // Expected position for calibration
                    //adjust_site,
                    // Calibration values
                    -27, 70, 0,
                    50, -40, -15,
                    -27,
                    // Physical lengths
                    65, {30.5f, 53.f, 79.5f},
                    // Speeds configuration
                    //300, 500, 250, 150
                    1000, 2000, 1000, 500
                    ){};
};
