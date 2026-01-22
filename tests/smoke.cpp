#include "engine/model/player.hpp"

#include <iostream>

int main() {
    Player p{"John Doe", 25, Handedness::RIGHT, Handedness::RIGHT, BatterRatings{0.5, 0.5, 0.5, 0.5, 0.5, 0.5}, std::nullopt, DefenseRatings{0.5, 0.5, 0.5, 0.5, 0.5}, std::nullopt, std::nullopt};
    std::cout << p.name << " " << p.age << " " << " " << " " << p.batterRatings.contact << " " << p.batterRatings.power << " " << p.batterRatings.eye << " " << p.batterRatings.speed << " " << p.batterRatings.ground_ball_tendency << " " << p.batterRatings.fly_ball_tendency << " " << p.defenseRatings.range << " " << p.defenseRatings.hands << " " << p.defenseRatings.infield_arm << " " << p.defenseRatings.outfield_arm << " " << p.defenseRatings.double_play << std::endl;
    (void)p;
    std::cout << "Smoke OK\n";
    return 0;
}

