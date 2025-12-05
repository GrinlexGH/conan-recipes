#include <steam/steam_api.h>
#include <iostream>

int main() {
    bool apiInit = SteamAPI_Init();
    std::cout << "SteamAPI_Init returned " << apiInit << std::endl;

    ISteamUser* steamUser = SteamUser();
    if (steamUser) {
        SteamAPICall_t call = steamUser->GetEncryptedAppTicket(nullptr, 0, nullptr); 
        std::cout << "GetEncryptedAppTicket returned " << call << std::endl;
        SteamAPI_Shutdown();
        return 0;
    } else {
        std::cerr << "SteamUser returned nullptr" << std::endl;
        SteamAPI_Shutdown();
        return 0;
    }
}
