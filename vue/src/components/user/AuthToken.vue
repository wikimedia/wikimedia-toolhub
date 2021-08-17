<template>
	<v-container>
		<v-row
			v-if="loaded"
			class="elevation-2 ma-1 mb-4"
		>
			<v-col
				v-if="authtoken !== null"
				cols="12"
			>
				<dl
					class="row ma-1 pa-1"
				>
					<dt class="me-2 font-weight-bold">{{ $t( 'authtoken-token' ) }}</dt>
					<dd>{{ authtoken }}</dd>
				</dl>
			</v-col>

			<v-col
				cols="12"
			>
				<v-btn
					v-if="authtoken !== null"
					color="error base100--text"
					@click="deleteAuthtoken"
				>
					<v-icon
						dark
						class="me-2"
					>
						mdi-delete
					</v-icon>
					{{ $t( 'delete' ) }}
				</v-btn>
				<v-btn
					v-else
					color="primary base100--text"
					@click="newAuthtoken"
				>
					<v-icon
						dark
						class="me-2"
					>
						mdi-plus
					</v-icon>
					{{ $t( 'authtoken-new' ) }}
				</v-btn>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
	name: 'AuthToken',
	data() {
		return {
			loaded: false
		};
	},
	computed: {
		...mapState( 'user', [ 'authtoken' ] )
	},
	methods: {
		...mapActions( 'user', [ 'deleteAuthtoken' ] ),
		getAuthtoken() {
			this.$store.dispatch( 'user/getAuthtoken' ).then( () => {
				this.loaded = true;
			} );
		},
		newAuthtoken() {
			this.deleteAuthtoken().then( () => {
				this.$store.dispatch( 'user/newAuthtoken' );
			} );
		}
	},
	mounted() {
		this.getAuthtoken();
	}
};
</script>
