#pragma once
#include <string>
#include <optional>


enum class HitterType { LineDrive, GroundBall, FlyBall, PopFly, Grounder, Flyer };
enum class Position { P, C, _1B, _2B, _3B, SS, LF, CF, RF, DH, INF_UTIL, OF_UTIL };
enum class Handedness { LEFT, RIGHT, SWITCH };
enum class PitchType { FASTBALL, SLIDER, CURVEBALL, CHANGEUP, CUTTER, SINKER, SPLITTER, KNUCKLEBALL };

struct BatterRatings {
    float contact;
    float power;
    float eye;
    float speed;
    float ground_ball_tendency;
    float fly_ball_tendency;
};

struct PitcherRatings {
    float stuff;
    float control;
    float movement;
    float stamina;
};

struct DefenseRatings {
    float range;
    float hands;
    float infield_arm;
    float outfield_arm; // general arm rating for power + accuracy
    float double_play;
};

struct CatcherRatings {
    float framing;
    float blocking;
    float pop_time;
    float game_call;
};

struct Pitch {
    float velocity;
    float movement;
    float control;
    float usage; // the vector of usagesmust sum to 1.0
};

struct PitchTypeRatings {
    std::optional<Pitch> fastball;
    std::optional<Pitch> slider;
    std::optional<Pitch> curveball;
    std::optional<Pitch> changeup;
    std::optional<Pitch> cutter;
    std::optional<Pitch> sinker;
    std::optional<Pitch> splitter;
    std::optional<Pitch> knuckleball;
};

struct Player {
    std::string name;
    int age;

    Handedness bats;
    Handedness throws; // also counts as pitching hand

    BatterRatings batterRatings;
    std::optional<PitcherRatings> pitcherRatings;
    DefenseRatings defenseRatings;

    // Optional ratings
    // Catcher
    std::optional<CatcherRatings> catcherRatings;

    // Pitcher
    std::optional<PitchTypeRatings> pitchTypeRatings;
};

