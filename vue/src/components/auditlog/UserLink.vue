<template>
	<div v-frag>
		<template v-if="user && user.username">
			<dd class="log-event-actor">
				<a
					:href="profileLink( user )"
					target="_blank"
				>{{ user.username }}</a>
			</dd>
			<dd v-if="showTalk"
				class="log-event-actor-talk"
			>
				(<a
					:href="talkLink( user )"
					target="_blank"
				>{{ $t( 'talk' ) }}</a>)
			</dd>
		</template>
		<template v-else>
			<dd class="log-event-actor">
				{{ $t( 'system-user' ) }}
			</dd>
		</template>
	</div>
</template>

<script>
export default {
	name: 'UserLink',
	props: {
		user: {
			type: Object,
			required: false,
			default: null
		},
		showTalk: {
			type: Boolean,
			required: false
		}
	},
	methods: {
		profileLink( user ) {
			return 'https://meta.wikimedia.org/wiki/User:' +
				encodeURIComponent( user.username );
		},
		talkLink( user ) {
			return 'https://meta.wikimedia.org/wiki/User_talk:' +
				encodeURIComponent( user.username );
		}
	}
};
</script>
