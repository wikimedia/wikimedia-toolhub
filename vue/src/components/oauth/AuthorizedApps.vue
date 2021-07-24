<template>
	<v-container>
		<v-row v-if="loaded">
			<v-col
				cols="12"
				class="text-h6 text--secondary"
			>
				<template
					v-if="!$can( 'add', 'oauth2_provider/application' )"
				>
					<span>{{ $t( 'developersettings-nologintext' ) }}</span>
				</template>

				<template
					v-else
				>
					<span v-if="numAuthorizedApps === 0">
						{{ $t( 'developersettings-noauthorizedappsfoundtext' ) }}
					</span>
				</template>
			</v-col>
		</v-row>

		<v-row v-for="app in authorizedApps"
			:key="app.id"
			class="elevation-2 ma-1 mb-4"
		>
			<v-col cols="12">
				<dl
					class="row ma-1 pa-1"
				>
					<dt class="me-2 font-weight-bold">{{ $t( 'appname' ) }}</dt>
					<dd>{{ app.application.name }}</dd>
				</dl>

				<dl
					class="row ma-1 pa-1"
				>
					<dt class="me-2 font-weight-bold">{{ $t( 'clientid' ) }}</dt>
					<dd>{{ app.application.client_id }}</dd>
				</dl>

				<dl
					class="row ma-1 pa-1"
				>
					<dt class="me-2 font-weight-bold">{{ $t( 'createdby' ) }}</dt>
					<dd>{{ app.application.user.username }}</dd>
				</dl>

				<dl
					class="row ma-1 pa-1"
				>
					<dt class="me-2 font-weight-bold">{{ $t( 'redirecturl' ) }}</dt>
					<dd>{{ app.application.redirect_url }}</dd>
				</dl>
			</v-col>

			<v-col cols="12">
				<v-btn
					color="error base100--text"
					@click="deleteAuthorizedApp( app.id )"
				>
					<v-icon
						dark
						class="me-2"
					>
						mdi-delete
					</v-icon>
					{{ $t( 'delete' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row v-if="pages > 1">
			<v-col cols="12">
				<v-pagination
					v-model="page"
					:length="pages"
					class="ma-4"
					total-visible="5"
					@input="goToPage"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';

export default {
	name: 'AuthorizedApps',
	data() {
		return {
			loaded: false,
			itemsPerPage: 10,
			page: 1
		};
	},
	computed: {
		...mapState( 'oauth', [ 'authorizedApps', 'numAuthorizedApps' ] ),
		pages() {
			return Math.ceil( this.numAuthorizedApps / this.itemsPerPage );
		}
	},
	methods: {
		listAuthorizedApps() {
			this.$store.dispatch(
				'oauth/listAuthorizedApps', this.page
			).then( () => {
				this.loaded = true;
			} );
		},
		deleteAuthorizedApp( id ) {
			return this.$store.dispatch( 'oauth/deleteAuthorizedApp', id );
		},
		goToPage( num ) {
			this.page = num;
			this.listAuthorizedApps();
		}
	},
	mounted() {
		this.listAuthorizedApps();
	}
};
</script>
