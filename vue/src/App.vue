<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
      dense
    >
      <v-app-bar-nav-icon></v-app-bar-nav-icon>
      <v-toolbar-title>Toolhub</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>

      <template v-slot:extension>
        <v-tabs
          v-model="tab"
          align-with-title
        >
          <v-tabs-slider color="secondary"></v-tabs-slider>
          <v-tab to="/">Home</v-tab>
          <v-tab to="/about">About</v-tab>
        </v-tabs>
      </template>

    </v-app-bar>

    <v-main>
      <v-container>
        <router-view/>
      </v-container>
    </v-main>
  </v-app>
</template>
