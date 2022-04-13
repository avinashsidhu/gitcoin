query = '''
    [].json[].{
        pk:pk, 
        url: url,
        paid: paid,
        network: network,
        title: title,
        status: status,
        is_open: is_open,
        keywords: keywords,
        project_type: project_type,
        experience_level: experience_level,
        permission_type: permission_type,
        github_url: github_url,
        github_repo_name: github_repo_name,
        github_comments: github_comments,
        github_issue_state: github_issue_state,
        token_name: token_name,
        value_in_usdt: value_in_usdt,
        value_true: value_true,
        value_in_eth: value_in_eth,
        value_in_token: value_in_token,
        created: web3_created,
        expires_date: expires_date,
        created_on: created_on,
        modified_on: modified_on,
        cancelled_on: cancelled_on,
        fulfillment_started_on: fulfillment_started_on,
        fulfillment_submitted_on: fulfillment_submitted_on,
        fulfillment_accepted_on: fulfillment_accepted_on,
        org_name: org_name,
        github_org_name: github_org_name,
        bounty_owner_name: bounty_owner_name,
        bounty_owner_email: bounty_owner_email,
        bounty_owner_address: bounty_owner_address,
        bounty_owner_github_username: bounty_owner_github_username,
        fulfillment:fulfillments[].{
            event_pk:pk, 
            tenant:tenant, 
            created:created_on, 
            token_name:token_name, 
            accepted_on:accepted_on,
            accepted:accepted, 
            payout_amount:payout_amount, 
            payout_status:payout_status,
            handle:profile.handle, 
            fulfiller_address:fulfiller_address, 
            hoursworked:fulfiller_metadata.data.payload.fulfiller.hoursWorked
            },
        interest: interested[].{
            event_pk:pk, 
            created:created, 
            handle:profile.handle
            },
        activity: activities[].{
            event_pk:pk, 
            created:created, 
            handle:profile.handle, 
            activity_type:activity_type
            }
        }
'''