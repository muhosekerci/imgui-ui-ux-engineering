void DrawBalancedFixture() {
    ImGui::PushID(42);
    ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1.0f, 1.0f, 1.0f, 1.0f));
    if (ImGui::Begin("Fixture")) {
        ImGui::TextUnformatted("Balanced");
    }
    ImGui::End();
    ImGui::PopStyleColor();
    ImGui::PopID();
}
