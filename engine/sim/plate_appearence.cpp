#include "engine/sim/plate_appearence.hpp"

#include <algorithm>

namespace {

float clamp(float v, float lo, float hi) {
    return std::max(lo, std::min(hi, v));
}

}  // namespace

PlateAppearance::PlateAppearance(const Player& batter, const Player& pitcher, RNG& rng) : batter_(&batter), pitcher_(&pitcher), rng_(&rng) {}

PlateAppearanceResult PlateAppearance::resolve() {
    const auto& bat = batter_->batterRatings.current;
    const auto& pit = pitcher_->pitcherRatings.current;

    // Outcome probabilities from ratings (all ratings in [0,1]; scale to plausible rates)
    float walk_prob = 0.12f * bat.eye * (1.0f - pit.control * 0.8f);
    float k_prob = 0.24f * (1.0f - bat.contact * 0.8f) * (0.3f + pit.stuff * 0.7f);
    float hr_prob = 0.04f * bat.power * (1.0f - pit.movement * 0.7f);

    walk_prob = clamp(walk_prob, 0.02f, 0.18f);
    k_prob = clamp(k_prob, 0.08f, 0.38f);
    hr_prob = clamp(hr_prob, 0.005f, 0.10f);

    float in_play_prob = 1.0f - walk_prob - k_prob - hr_prob;
    in_play_prob = clamp(in_play_prob, 0.35f, 0.90f);

    // Renormalize so they sum to 1
    float total = walk_prob + k_prob + hr_prob + in_play_prob;
    walk_prob /= total;
    k_prob /= total;
    hr_prob /= total;
    in_play_prob /= total;

    float u = rng_->uniform();

    if (u < walk_prob) return PlateAppearanceResult::WALK;
    u -= walk_prob;
    if (u < k_prob) return PlateAppearanceResult::STRIKEOUT;
    u -= k_prob;
    if (u < hr_prob) return PlateAppearanceResult::HOMERUN;
    return PlateAppearanceResult::IN_PLAY;
}
