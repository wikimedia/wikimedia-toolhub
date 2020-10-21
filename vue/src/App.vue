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

      <UserStatus />

      <template v-slot:extension>
      <v-tabs
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

<script>
import UserStatus from "@/components/user/Status"
export default {
  components: {
    UserStatus
  },
  created() {
    console.log("App.vue created() called");
    this.$store.dispatch('getUserInfo');
  }
}
</script>
