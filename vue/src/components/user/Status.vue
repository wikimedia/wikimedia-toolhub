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
					aria-label="My Account"
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
				<v-list-item-avatar>
					<v-icon>mdi-account-circle</v-icon>
				</v-list-item-avatar>
				<v-list-item-content>
					<v-list-item-title>
						{{ user.username }}
					</v-list-item-title>
				</v-list-item-content>
			</v-list-item>
			<v-divider />
			<v-list-item
				href="/user/logout/"
				link
			>
				<v-list-item-icon>
					<v-icon>mdi-logout</v-icon>
				</v-list-item-icon>
				<v-list-item-content>
					<v-list-item-title>
						Logout
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
		v-bind="attrs"
		v-on="on"
		@click="loading = true"
	>
		Login
		<v-icon>mdi-login</v-icon>
	</v-btn>
</template>

<script>
import { mapState } from 'vuex';
export default {
	name: 'UserStatus',
	data() {
		return {
			attrs: '',
			loading: false,
			on: ''
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
