<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'members' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'members-pagetitle' ) }}</p>
			</v-col>
		</v-row>

		<v-form ref="filtersform">
			<v-row>
				<v-col cols="6"
					md="4"
				>
					<v-text-field
						v-model="filters.username"
						:label="$t( 'members-userslist-header-username' )"
						prepend-icon="mdi-account-outline"
					/>
				</v-col>

				<v-col cols="6"
					md="4"
				>
					<v-select
						v-model="filters.groups_id"
						:label="$t( 'members-groupselect-label' )"
						:items="groups"
						item-text="name"
						item-value="id"
						prepend-icon="mdi-filter-variant"
					/>
				</v-col>

				<v-col cols="6"
					md="2"
					class="mt-2"
				>
					<v-btn
						color="primary base100--text"
						block
						@click="filterUsers"
					>
						{{ $t( 'filter' ) }}
						<v-icon
							dark
							right
						>
							mdi-magnify
						</v-icon>
					</v-btn>
				</v-col>
				<v-col cols="6"
					md="2"
					class="mt-2"
				>
					<v-btn
						block
						@click="clearFilters"
					>
						{{ $t( 'clear' ) }}
						<v-icon
							dark
							right
						>
							mdi-close
						</v-icon>
					</v-btn>
				</v-col>
			</v-row>
		</v-form>

		<v-row
			class="my-4"
		>
			<v-col cols="12">
				<v-data-table
					:items-per-page="itemsPerPage"
					:headers="usersListHeaders"
					:items="users"
					class="elevation-2 mt-2"
					hide-default-footer
					mobile-breakpoint="0"
					:loading="numUsers === 0"
				>
					<template #[`item.username`]="{ item }">
						<a :href="`http://meta.wikimedia.org/wiki/User:${item.username}`" target="_blank">{{ item.username
						}}</a>
					</template>
					<template #[`item.date_joined`]="{ item }">
						{{ item.date_joined | moment( 'lll' ) }}
					</template>
					<template #[`item.groups`]="{ item }">
						<v-chip
							v-for="group in item.groups"
							:key="group.name"
							:ripple="false"
							disabled
							class="ma-1 opacity-1"
						>
							{{ group.name }}
						</v-chip>
					</template>
					<template #[`item.add_remove_member`]="{ item }">
						<v-btn
							class="mt-2 mb-2"
							color="primary base100--text"
							@click="invokeDialog( item )"
						>
							<v-icon
								dark
							>
								mdi-pencil
							</v-icon>
						</v-btn>
					</template>
				</v-data-table>

				<v-pagination
					v-if="numUsers > 0"
					v-model="page"
					:length="Math.ceil( numUsers / itemsPerPage )"
					class="ma-4"
					@input="goToPage"
				/>
			</v-col>
		</v-row>

		<v-dialog
			ref="dialog"
			v-model="dialog.open"
			persistent
			max-width="600px"
			@keydown.esc="dialog.open = false"
		>
			<v-card>
				<v-card-title>
					<span class="text-h5">{{ $t( 'members-dialog-title',
						[ dialog.user.username ] ) }}</span>
				</v-card-title>

				<v-card-text>
					<v-container>
						<v-row v-if="notification !== null">
							<v-col cols="12">
								<v-alert
									:type="notification.type"
									dismissible
									@input="clearNotification"
								>
									{{ notification.message }}
								</v-alert>
							</v-col>
						</v-row>
						<v-row>
							<v-col cols="9">
								<v-select
									ref="groupFilterForSelectedUser"
									v-model="groupFilterForSelectedUser"
									:items="filteredGroupsForSelectedUser"
									item-value="name"
									item-text="name"
									:label="$t( 'members-groupselect-label' )"
								/>
							</v-col>

							<v-col cols="3">
								<v-btn
									class="mt-4"
									color="primary base100--text"
									width="100%"
									block
									:disabled="groupFilterForSelectedUser === ''"
									@click="addMemberToGroup( dialog.user )"
								>
									{{ $t( 'add' ) }}
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
							<v-col cols="12">
								<v-data-table
									:items-per-page="itemsPerPage"
									:headers="userGroupsListHeaders"
									:items="dialog.user.groups"
									class="elevation-2 mt-2"
									hide-default-footer
									mobile-breakpoint="0"
									:loading="dialog.user.groups === 0"
								>
									<template #[`item.groups`]="{ item }">
										{{ item.name }}
									</template>
									<template #[`item.remove_member`]="{ item }">
										<v-btn
											class="mt-2 mb-2"
											color="error"
											@click="removeMemberFromGroup( dialog.user, item )"
										>
											<v-icon
												dark
											>
												mdi-delete
											</v-icon>
										</v-btn>
									</template>
								</v-data-table>
							</v-col>
						</v-row>
					</v-container>
				</v-card-text>

				<v-card-actions>
					<v-spacer />

					<v-btn
						color="accent text--secondary"
						@click="close"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-close
						</v-icon>
						{{ $t( 'close' ) }}
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import { filterEmpty } from '@/helpers/object';

export default {
	name: 'Members',
	data() {
		return {
			page: 1,
			itemsPerPage: 10,
			dialog: {
				user: {},
				open: false
			},
			filters: {
				username: null,
				groups_id: null
			},
			groupFilterForSelectedUser: '',
			filteredGroupsForSelectedUser: []
		};
	},
	computed: {
		...mapState( 'user', [ 'users', 'numUsers' ] ),
		...mapState( 'groups', [ 'groups', 'numGroups', 'notification' ] ),

		usersListHeaders() {
			const headers = [
				{
					text: this.$t( 'members-userslist-header-username' ),
					value: 'username',
					sortable: true
				},
				{
					text: this.$t( 'members-userslist-header-membersince' ),
					value: 'date_joined',
					sortable: true
				},
				{
					text: this.$t( 'members-userslist-header-groups' ),
					value: 'groups',
					sortable: false
				}
			];

			if ( this.$can( 'change', 'auth/group' ) ) {
				headers.push( {
					text: this.$t( 'members-userslist-header-action' ),
					value: 'add_remove_member',
					sortable: false,
					align: 'right'
				} );
			}

			return headers;
		},

		userGroupsListHeaders() {
			return [
				{
					text: this.$t( 'members-usergroupslist-header-groups' ),
					value: 'groups',
					sortable: false
				},
				{
					text: this.$t( 'members-usergroupslist-header-removemember' ),
					value: 'remove_member',
					sortable: false,
					align: 'right'
				}
			];
		}
	},
	methods: {
		listAllUsers() {
			this.$store.dispatch( 'user/listAllUsers', {
				page: this.page,
				filters: this.filters
			} ).then( () => {
				this.$router.push( {
					name: 'members',
					query: filterEmpty( this.filters )
				} ).catch( () => {} );
			} );
		},
		listAllUserGroups() {
			this.$store.dispatch( 'groups/listAllUserGroups', /* page */ 1 );
		},
		addMemberToGroup( member ) {
			const selectedGroup = this.groups.find( ( group ) =>
				group.name === this.groupFilterForSelectedUser );
			this.$store.dispatch( 'groups/addMemberToGroup', {
				group: selectedGroup,
				member: member
			} );
			this.groupFilterForSelectedUser = '';
			this.$refs.groupFilterForSelectedUser.reset();
		},
		removeMemberFromGroup( member, group ) {
			this.$store.dispatch( 'groups/removeMemberFromGroup', {
				group: group,
				member: member
			} );
		},
		goToPage( num ) {
			this.page = num;
			this.listAllUsers();
		},
		setFilteredGroups() {
			this.filteredGroupsForSelectedUser = this.groups.filter(
				( group ) => !this.dialog.user.groups.filter(
					( selectedUserGroup ) => selectedUserGroup.id === group.id
				).length
			);
		},
		invokeDialog( user ) {
			this.dialog = {
				open: true,
				user: user
			};
			this.setFilteredGroups();
		},
		clearNotification() {
			this.$store.commit( 'groups/NOTIFICATION', null );
		},
		close() {
			this.dialog.open = false;
			this.clearNotification();
		},
		filterUsers() {
			this.page = 1;
			this.listAllUsers();
		},
		clearFilters() {
			this.$refs.filtersform.reset();
			this.listAllUsers();
		},
		/**
		 * Allow deep linking to filtered results by reconstructing internal
		 * state based on data provided in the current query string.
		 *
		 * @return {boolean} True if state was updated. False otherwise.
		 */
		loadStateFromQueryString() {
			const params = new URLSearchParams(
				document.location.search.substring( 1 )
			);
			let gotQueryData = false;
			for ( const [ key, value ] of params ) {
				if ( value === undefined ) {
					continue;
				}
				switch ( key ) {
					case 'username':
						this.filters.username = value;
						gotQueryData = true;
						break;
					case 'groups_id':
						this.filters.groups_id = value;
						gotQueryData = true;
						break;
					case 'page':
						this.page = parseInt( value, 10 );
						gotQueryData = true;
						break;
					default:
						// ignore this param
						break;
				}
			}
			return gotQueryData;
		}
	},
	watch: {
		users: {
			handler( newUsers ) {
				if ( this.dialog.open ) {
					this.dialog.user = newUsers.find( ( user ) => user.id === this.dialog.user.id );
					this.setFilteredGroups();
				}
			},
			deep: true,
			immediate: true
		}
	},
	mounted() {
		this.loadStateFromQueryString();
		this.listAllUserGroups();
		this.listAllUsers();
	}
};
</script>
