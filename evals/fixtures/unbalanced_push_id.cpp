void DrawUnbalancedFixture() {
    ImGui::PushID(42);
    if (ImGui::Begin("Fixture")) {
        ImGui::TextUnformatted("This fixture intentionally omits PopID().");
    }
    ImGui::End();
}
