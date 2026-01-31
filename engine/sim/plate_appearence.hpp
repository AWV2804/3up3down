#pragma once

#include "engine/core/rng.hpp"
#include "engine/model/player.hpp"

enum class PlateAppearanceResult {
    WALK,
    STRIKEOUT,
    HOMERUN,
    IN_PLAY
};

class PlateAppearance {
public:
    PlateAppearance(
        const Player& batter,
        const Player& pitcher,
        RNG& rng);

    PlateAppearanceResult resolve();

private:
    const Player* batter_;
    const Player* pitcher_;
    RNG* rng_;
};
