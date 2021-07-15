<template>
	<v-menu
		v-if="user.is_authenticated"
		offset-y
	>
		<template #activator="{ on, attrs }">
			<v-btn
				class="ma-1 white-text"
				color="secondary"
				v-bind="attrs"
				v-on="on"
			>
				<v-icon
					:aria-label="$t( 'my-account' )"
					role="img"
					aria-hidden="false"
				>
					mdi-account-circle
				</v-icon>
			</v-btn>
		</template>
		<v-list
			dense
			nav
		>
			<v-list-item>
				<v-list-item-icon>
					<v-icon>mdi-account-circle</v-icon>
				</v-list-item-icon>
				<v-list-item-content>
					<v-list-item-title>
						{{ user.username }}
					</v-list-item-title>
				</v-list-item-content>
			</v-list-item>
			<v-list-item
				to="/developer-settings"
			>
				<v-list-item-icon>
					<v-icon>mdi-file-code</v-icon>
				</v-list-item-icon>
				<v-list-item-content>
					<v-list-item-title>
						{{ $t( 'developersettings' ) }}
					</v-list-item-title>
				</v-list-item-content>
			</v-list-item>
			<v-divider />
			<v-list-item
				href="/user/logout/"
			>
				<v-list-item-icon>
					<v-icon>mdi-logout</v-icon>
				</v-list-item-icon>
				<v-list-item-content>
					<v-list-item-title>
						{{ $t( "logout" ) }}
					</v-list-item-title>
				</v-list-item-content>
			</v-list-item>
		</v-list>
	</v-menu>
	<v-btn
		v-else
		class="ma-1 white-text"
		color="secondary"
		:href="loginHref"
		:disabled="loading"
		:loading="loading"
		@click="loading = true"
	>
		{{ $t( "login" ) }}
		<v-icon>mdi-login</v-icon>
	</v-btn>
</template>

<script>
import { mapState } from 'vuex';
export default {
	name: 'UserStatus',
	data() {
		return {
			loading: false
		};
	},
	computed: {
		...mapState( 'user', [ 'user' ] ),
		loginHref() {
			return '/user/login/?next=' + this.$route.path;
		}
	}
};
</script>
