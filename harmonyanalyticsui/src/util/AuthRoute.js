import React from "react";
import { Route, Redirect } from "react-router-dom";

export default ({ component: C, props: cProps, ...rest }) => {
  // console.log("AuthRoute: cProps.isAuthenticated - " + cProps.isAuthenticated);
  return (
    <Route {...rest} render={props =>
        cProps.isAuthenticated ? <C {...props} {...cProps} />
          : <Redirect to={`/login?redirect=${props.location.pathname}${props.location.search}`} />
      }
    />
  );
}
