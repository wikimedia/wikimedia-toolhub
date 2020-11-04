<template>
	<v-app>
		<v-app-bar
			app
			color="primary"
			dark
			dense
			flat
			clipped-left
			clipped-right
			tile
		>
			<v-app-bar-nav-icon
				v-if="$vuetify.breakpoint.smAndDown"
				@click.stop="drawer = !drawer"
			/>
			<v-app-bar-nav-icon
				v-if="$vuetify.breakpoint.mdAndUp"
			>
				<v-img
					src="/static/img/logo-solid-grey.svg"
					alt="Toolforge logo"
					aria-hidden="true"
					class="ma-1"
					aspect-ratio="1.0"
					contain
				/>
			</v-app-bar-nav-icon>
			<v-toolbar-title class="font-weight-bold">
				Toolhub
			</v-toolbar-title>

			<v-spacer />

			<UserStatus />
		</v-app-bar>

		<v-navigation-drawer
			v-model="drawer"
			app
			color="secondary"
			dark
			clipped
			:permanent="$vuetify.breakpoint.mdAndUp"
			:expand-on-hover="$vuetify.breakpoint.mdAndUp && drawer"
		>
			<v-list
				dense
				nav
			>
				<v-list-item
					v-for="route in this.$router.options.routes"
					:key="route.name"
					:to="route.path"
					link
				>
					<v-list-item-icon>
						<v-icon>{{ route.meta.icon }}</v-icon>
					</v-list-item-icon>
					<v-list-item-content>
						<v-list-item-title>{{ route.title }}</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
			</v-list>
		</v-navigation-drawer>

		<v-main>
			<v-container fluid>
				<router-view />
			</v-container>
		</v-main>

		<v-footer app />
	</v-app>
</template>

<script>
import UserStatus from '@/components/user/Status';
export default {
	components: {
		UserStatus
	},
	data() {
		return {
			drawer: true
		};
	},
	created() {
		this.$store.dispatch( 'getUserInfo' );
	}
};
</script>
