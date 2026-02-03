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

    // pa_outcome_rates_same.json
    const float base_walk_prob_same = 0.07222732043455087f;
    const float base_hbp_prob_same = 0.012946406492985531f;
    const float base_single_prob_same = 0.14511405036789554f;
    const float base_double_prob_same = 0.04112517240810854f;
    const float base_triple_prob_same = 0.0032091262274633065f;
    const float base_hr_prob_same = 0.028288667498255312f;
    const float base_strikeout_prob_same = 0.23013941015820333f;
    const float base_out_prob_same = 0.46694984641253756f;

    // pa_outcome_rates_opposite.json
    const float base_walk_prob_alt = 0.08774304988212227f;
    const float base_hbp_prob_alt = 0.009042739431852664f;
    const float base_single_prob_alt = 0.13974930557176538f;
    const float base_double_prob_alt = 0.0437431432506244f;
    const float base_triple_prob_alt = 0.004075535118227866f;
    const float base_hr_prob_alt = 0.03190868560491118f;
    const float base_strikeout_prob_alt = 0.2188651058565393f;
    const float base_out_prob_alt = 0.46487243528395694f;

    // Outcome probabilities from 2024-2025 seasons incl.
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
