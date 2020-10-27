<template>
  <v-container>
    <v-row>
      <v-col
        md="8"
        cols="12"
        order-md="1"
        order="2"
      >
        <!--start add or remove tools section-->
        <v-row>
          <h2 class="display-1">
            {{ $vuetify.lang.t('$vuetify.addremovetools-pagetitle') }}
          </h2>
        </v-row>
        <v-row>
          <v-col
            lg="8"
            sm="10"
            cols="9"
            class="pl-0"
          >
            <v-text-field
              ref="url"
              v-model="fileUrl"
              :label="$vuetify.lang.t('$vuetify.jsonfileurl')"
              prepend-icon="mdi-link-variant"
              :rules="urlRules"
              required
            />
          </v-col>
          <v-col
            lg="2"
            sm="2"
            cols="3"
          >
            <v-btn
              class="mt-4"
              color="primary"
              dark
              width="100%"
              @click="addToolFile(fileUrl)"
            >
              {{ $vuetify.lang.t('$vuetify.add') }}
              <v-icon
                dark
                right
              >
                mdi-checkbox-marked-circle
              </v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col
            lg="10"
            cols="12"
          >
            <v-simple-table
              v-if="allToolFiles.length > 0"
              class="elevation-2"
            >
              <template #default>
                <thead>
                  <tr>
                    <th class="text-left">
                      {{ $vuetify.lang.t('$vuetify.jsonfileurl') }}
                    </th>
                    <th class="text-right">
                      {{ $vuetify.lang.t('$vuetify.removeurl') }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="toolFileUrl in allToolFiles"
                    :key="toolFileUrl"
                  >
                    <td class="text-left">
                      <a
                        :href="toolFileUrl"
                        target="_blank"
                      >{{ toolFileUrl }}</a>
                    </td>
                    <td class="text-right">
                      <v-btn
                        class="mt-2 mb-2"
                        color="error"
                        dark
                        @click="removeToolFile(toolFileUrl)"
                      >
                        <v-icon
                          dark
                        >
                          mdi-delete-circle
                        </v-icon>
                      </v-btn>
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
            <v-alert
              v-if="$store.state.user.is_authenticated === true && allToolFiles.length == 0"
              type="error"
              border="left"
              elevation="2"
              width="100%"
            >
              {{ $vuetify.lang.t('$vuetify.nourlsfounderror') }}
            </v-alert>
          </v-col>
        </v-row>
      </v-col> <!--end add or remove tools section-->
      <v-col
        md="4"
        cols="12"
        order-md="2"
        order="1"
      >
        <!--start how this page works section-->
        <v-row>
          <v-alert
            color="primary"
            border="top"
            colored-border
            elevation="2"
          >
            <h3 class="headline">
              {{ $vuetify.lang.t('$vuetify.addremovetools-summarytitle') }}
            </h3>
            <v-divider class="pa-2" />
            <p>
              {{ $vuetify.lang.t('$vuetify.addremovetools-summary') }}
              <a
                href="https://meta.wikimedia.org/wiki/Toolhub/Data_model#Version_1.2.0"
                target="_blank"
              >{{ $vuetify.lang.t('$vuetify.schemalink') }}</a>.
            </p>
          </v-alert>
        </v-row>
        <v-row cols="12">
          <v-alert
            v-if="$store.state.user.is_authenticated === false"
            border="left"
            color="primary"
            dark
            elevation="2"
            type="info"
            width="100%"
          >
            {{ $vuetify.lang.t('$vuetify.addremovetools-nologintext') }}
          </v-alert>
        </v-row>
      </v-col> <!--end how this page works section-->
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
	data() {
		return {
			fileUrl: '',
			urlRegex: new RegExp( '^(https?:\\/\\/)?((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' +
      '((\\d{1,3}\\.){3}\\d{1,3}))(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*(\\?[;&a-z\\d%_.~+=-]*)?' +
      '(\\#[-a-z\\d_]*)?$', 'i' ), // Taken from https://stackoverflow.com/a/5717133
			urlRules: [
				( v ) => !!v || this.$vuetify.lang.t( '$vuetify.urlrequired' ),
				( v ) => this.urlRegex.test( v ) || this.$vuetify.lang.t( '$vuetify.urlinvalid' )
			]
		};
	},
	computed: {
		...mapGetters( [ 'allToolFiles' ] )
	},
	methods: {
		addToolFile: function ( file ) {
			if ( !this.fileUrl || !this.urlRegex.test( this.fileUrl ) ) {
				this.$refs.url.validate( true );
				return;
			}
			this.$store.dispatch( 'addToolFile', file );
			this.fileUrl = '';
			this.$refs.url.reset();
		},
		removeToolFile: function ( file ) {
			this.$store.dispatch( 'removeToolFile', file );
		}
	}
};
</script>
