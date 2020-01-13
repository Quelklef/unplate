import sys
sys.path.append('..')
import unplate


# Unplate offers configuration of its syntax.
# The coolest option is offers is the
# ability to change the syntax for marking
# a template. By default, it's
#   unplate.template( TEMPLATE )
# But we can make it whatever we want.
# For instance, let's make it:
#   ({[ TEMPLATE ]})

# Changing this option MUST come before
# the exec() call.

unplate.options.pattern = '({[\nTEMPLATE\n]})'
exec(unplate.transform_file(__file__))

# The leading and trailing newline are required
# because templates are on their own line, since
# they are comments.
# Now we can make templates
# like this:

my_template = ({[
  # Fancy syntax!
  # Using this syntax is not recommended, since
  # it may class with normal code.
  # However, changing it to something like
  #   my_template(TEMPLATE)
  # is fine.
]})

print(my_template)

# Note that any custom syntax MUST be lexable by
# the normal Python grammar. This is because Unplate
# operates on the token level rather than the string
# level.
# So, for instance, the syntax
#   my_template( TEMPLATE ]
# will not work beause the brackets do not match.
