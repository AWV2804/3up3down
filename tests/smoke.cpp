#include "engine/model/player.hpp"

#include <iostream>

int main() {
    BatterRatings bat{0.5f, 0.5f, 0.5f, 0.5f, 0.5f, 0.5f};
    PitcherRatings pit{0.5f, 0.5f, 0.5f, 0.5f};
    DefenseRatings def{0.5f, 0.5f, 0.5f, 0.5f, 0.5f};
    CatcherRatings cat{0.5f, 0.5f, 0.5f, 0.5f};

    Player p{
        "John Doe",
        25,
        false,   // is_pitcher
        false,   // is_two_way_player
        Handedness::RIGHT,
        Handedness::RIGHT,
        Ratings<BatterRatings>{bat, bat},
        Ratings<PitcherRatings>{pit, pit},
        Ratings<DefenseRatings>{def, def},
        Ratings<CatcherRatings>{cat, cat},
        std::nullopt  // pitchTypeRatings
    };

    const auto& c = p.batterRatings.current;
    const auto& d = p.defenseRatings.current;
    std::cout << p.name << " " << p.age << " " << c.contact << " " << c.power << " " << c.eye << " " << c.speed << " " << c.ground_ball_tendency << " " << c.fly_ball_tendency << " " << d.range << " " << d.hands << " " << d.infield_arm << " " << d.outfield_arm << " " << d.double_play << std::endl;
    std::cout << "Smoke OK\n";
    return 0;
}
