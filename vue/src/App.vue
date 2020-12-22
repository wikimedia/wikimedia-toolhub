<template>
	<v-app>
		<v-app-bar
			app
			color="primary"
			dark
			flat
			tile
		>
			<v-app-bar-nav-icon
				v-if="$vuetify.breakpoint.smAndDown"
				@click.stop="drawer = !drawer"
			/>

			<v-spacer />
			<SelectLocale />
			<UserStatus />
		</v-app-bar>

		<v-navigation-drawer
			v-model="drawer"
			app
			color="secondary"
			dark
			:floating="true"
			:permanent="$vuetify.breakpoint.mdAndUp"
			:expand-on-hover="$vuetify.breakpoint.mdAndUp && drawer"
			:right="$vuetify.rtl"
		>
			<v-list-item class="ms-2 mt-1 ps-1">
				<v-list-item-avatar
					size="35"
					class="me-4"
				>
					<v-img
						src="/static/img/logo-solid-white.svg"
						alt="Toolforge logo"
					/>
				</v-list-item-avatar>

				<v-list-item-content class="mt-1">
					<v-list-item-title class="font-weight-bold">
						Toolhub
					</v-list-item-title>
				</v-list-item-content>

				<v-btn
					v-if="$vuetify.breakpoint.smAndDown"
					icon
					@click.stop="drawer = !drawer"
				>
					<v-icon>mdi-chevron-left</v-icon>
				</v-btn>
			</v-list-item>

			<v-divider class="mt-2" />

			<v-list
				dense
				nav
			>
				<v-list-item
					v-for="route in routes"
					:key="route.name"
					:to="route.path"
					link
					exact
				>
					<v-list-item-icon>
						<v-icon>{{ route.meta.icon }}</v-icon>
					</v-list-item-icon>
					<v-list-item-content>
						<v-list-item-title>{{ $t( route.name ) }}</v-list-item-title>
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
import { mapState } from 'vuex';
import UserStatus from '@/components/user/Status';
import SelectLocale from '@/components/locale/SelectLocale';
import { getLangNameFromCode } from 'language-name-map';

export default {
	components: {
		UserStatus,
		SelectLocale
	},
	data() {
		return {
			drawer: false
		};
	},
	computed: {
		...mapState( 'user', [] ),
		routes() {
			return this.$router.options.routes.filter(
				( route ) => ( route.meta !== undefined )
			);
		}
	},
	methods: {
		changeRTL() {
			const curLocale = this.$i18n.locale,
				curLocaleDir = getLangNameFromCode( curLocale ).dir;
			this.$vuetify.rtl = ( curLocaleDir === 0 );
		}
	},
	created() {
		this.$store.dispatch( 'user/getUserInfo' );
		this.changeRTL();
	}
};
</script>
